import { useEffect, useMemo, useRef, useState } from "react";

import type { ExternalLink, MapProjectionFeature } from "../../api/client";

const BRIDGE_CONTRACT = "orientation.host-bridge";
const BRIDGE_VERSION = "1.0";
const SOURCE_REF = "vocation.map_projection";
const DETAILS_ACTION = "details";
const OPEN_PREFERRED_ACTION = "open-preferred";
const OPEN_POSTING_PREFIX = "open-posting:";

export type OrientationMapAction = Readonly<{
  opportunityId: string;
  kind: "details" | "open-preferred" | "open-posting";
  postingId?: string;
}>;

type OrientationMapFrameProps = Readonly<{
  features: readonly MapProjectionFeature[];
  externalLinksByOpportunity: Readonly<Record<string, readonly ExternalLink[]>>;
  externalLinksLoaded: ReadonlySet<string>;
  externalLinkErrors: Readonly<Record<string, string>>;
  onAction: (action: OrientationMapAction) => void;
  onHostError: (message: string) => void;
}>;

type BridgeEnvelope = Readonly<{
  contract: string;
  version: string;
  type: string;
  payload: Record<string, unknown>;
}>;

function precisionLabel(precision: string): string {
  const labels: Record<string, string> = {
    exact_address: "Exakte Adresse",
    site: "Standort",
    city: "Stadt",
    region: "Region",
    approximate: "Ungefähr",
    unknown: "Unbekannt",
  };
  return labels[precision] ?? precision;
}

function availabilityLabel(availability: string): string {
  const labels: Record<string, string> = {
    available: "Verfügbar",
    unavailable: "Nicht verfügbar",
    uncertain: "Unsicher",
    unknown: "Unbekannt",
  };
  return labels[availability] ?? availability;
}

function sourceActionLabel(link: ExternalLink): string {
  return link.display_label
    ? `Quelle öffnen · ${link.source_name} · ${link.display_label}`
    : `Quelle öffnen · ${link.source_name}`;
}

export function buildOrientationScene(
  features: readonly MapProjectionFeature[],
  externalLinksByOpportunity: Readonly<Record<string, readonly ExternalLink[]>>,
  externalLinksLoaded: ReadonlySet<string>,
  externalLinkErrors: Readonly<Record<string, string>>,
) {
  return {
    features: features.map((feature) => {
      const links = externalLinksByOpportunity[feature.opportunity_id] ?? [];
      const informationRows = [
        { label: "Company", value: feature.company_name },
        { label: "Location", value: feature.location_label },
        { label: "Precision", value: precisionLabel(feature.precision) },
        { label: "Status", value: feature.tracking_status },
        {
          label: "Availability",
          value: availabilityLabel(feature.availability),
        },
        ...(feature.groups.length > 0
          ? [
              {
                label: "Groups/Waves",
                value: feature.groups.map((group) => group.name).join(" · "),
              },
            ]
          : []),
        ...(!externalLinksLoaded.has(feature.opportunity_id)
          ? [{ label: "Originalanzeigen", value: "Werden geladen …" }]
          : []),
        ...(externalLinkErrors[feature.opportunity_id]
          ? [
              {
                label: "Originalanzeigen",
                value: externalLinkErrors[feature.opportunity_id]!,
              },
            ]
          : []),
      ];

      const actions = [
        { ref: DETAILS_ACTION, label: "Details" },
        ...(links.length > 0
          ? [{ ref: OPEN_PREFERRED_ACTION, label: "Originalanzeige öffnen" }]
          : []),
        ...(links.length > 1
          ? links.map((link) => ({
              ref: `${OPEN_POSTING_PREFIX}${link.posting_id}`,
              label: sourceActionLabel(link),
            }))
          : []),
      ];

      return {
        ref: feature.feature_id,
        sourceRef: SOURCE_REF,
        coordinate: {
          longitude: feature.longitude,
          latitude: feature.latitude,
        },
        title: feature.title,
        subtitle: `${feature.company_name} · ${feature.location_label}`,
        information: [{ title: "Vocation", rows: informationRows }],
        actions,
      };
    }),
    viewport: {
      kind: "automatic",
      padding: 48,
      maxZoom: 15,
    },
  } as const;
}

function parseBridgeEnvelope(value: unknown): BridgeEnvelope | null {
  if (!value || typeof value !== "object") return null;
  const envelope = value as Record<string, unknown>;
  if (
    envelope.contract !== BRIDGE_CONTRACT ||
    envelope.version !== BRIDGE_VERSION ||
    typeof envelope.type !== "string" ||
    !envelope.payload ||
    typeof envelope.payload !== "object" ||
    Array.isArray(envelope.payload)
  ) {
    return null;
  }
  return envelope as BridgeEnvelope;
}

export function OrientationMapFrame({
  features,
  externalLinksByOpportunity,
  externalLinksLoaded,
  externalLinkErrors,
  onAction,
  onHostError,
}: OrientationMapFrameProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [bridgeReady, setBridgeReady] = useState(false);
  const featureByRef = useMemo(
    () => new Map(features.map((feature) => [feature.feature_id, feature])),
    [features],
  );
  const scene = useMemo(
    () =>
      buildOrientationScene(
        features,
        externalLinksByOpportunity,
        externalLinksLoaded,
        externalLinkErrors,
      ),
    [
      features,
      externalLinksByOpportunity,
      externalLinksLoaded,
      externalLinkErrors,
    ],
  );

  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const iframeWindow = iframeRef.current?.contentWindow;
      if (
        !iframeWindow ||
        event.source !== iframeWindow ||
        typeof event.data !== "string"
      )
        return;

      let parsed: unknown;
      try {
        parsed = JSON.parse(event.data);
      } catch {
        onHostError("Orientation hat eine ungültige Host-Nachricht geliefert.");
        return;
      }

      const envelope = parseBridgeEnvelope(parsed);
      if (!envelope) return;

      if (envelope.type === "bridge.ready") {
        setBridgeReady(true);
        onHostError("");
        return;
      }
      if (envelope.type === "bridge.error") {
        onHostError("Orientation hat den aktuellen Karteninhalt abgelehnt.");
        return;
      }
      if (envelope.type === "map.status") {
        if (envelope.payload.status === "ready") {
          onHostError("");
        } else if (envelope.payload.status === "error") {
          onHostError("Orientation-Kartenrendering ist nicht verfügbar.");
        }
        return;
      }
      if (envelope.type !== "action.activated") return;

      const featureRef = envelope.payload.featureRef;
      const sourceRef = envelope.payload.sourceRef;
      const actionRef = envelope.payload.actionRef;
      if (
        typeof featureRef !== "string" ||
        sourceRef !== SOURCE_REF ||
        typeof actionRef !== "string"
      ) {
        return;
      }

      const feature = featureByRef.get(featureRef);
      if (!feature) return;

      if (actionRef === DETAILS_ACTION) {
        onAction({ opportunityId: feature.opportunity_id, kind: "details" });
      } else if (actionRef === OPEN_PREFERRED_ACTION) {
        onAction({
          opportunityId: feature.opportunity_id,
          kind: "open-preferred",
        });
      } else if (actionRef.startsWith(OPEN_POSTING_PREFIX)) {
        const postingId = actionRef.slice(OPEN_POSTING_PREFIX.length);
        if (postingId) {
          onAction({
            opportunityId: feature.opportunity_id,
            kind: "open-posting",
            postingId,
          });
        }
      }
    }

    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [featureByRef, onAction, onHostError]);

  useEffect(() => {
    if (!bridgeReady) return;
    const target = iframeRef.current?.contentWindow;
    if (!target) return;
    target.postMessage(
      JSON.stringify({
        contract: BRIDGE_CONTRACT,
        version: BRIDGE_VERSION,
        type: "scene.replace",
        payload: scene,
      }),
      "*",
    );
  }, [bridgeReady, scene]);

  return (
    <iframe
      ref={iframeRef}
      className="opportunity-map"
      src="/orientation-map/embed.html"
      title="Vocation Opportunities map"
    />
  );
}
