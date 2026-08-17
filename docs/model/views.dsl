container vocation VocationContainers {
    include browserUi
    include applicationHost
    include sqliteStore
    include documentStore
    autolayout tb 180 120
    title "Vocation — Containers"
    description "Accepted local Vocation runtime and persistence boundaries."
}

styles {
    element "Vocation Browser UI" {
            shape Box
            background #F7F7F5
            color #1F2933
            stroke #4B5563
            strokeWidth 1
            description false
    }
    element "Vocation Application Host" {
            shape Box
            background #F7F7F5
            color #1F2933
            stroke #4B5563
            strokeWidth 1
            description false
    }
    element "Vocation Relational Store" {
            shape Cylinder
            background #F7F7F5
            color #1F2933
            stroke #4B5563
            strokeWidth 1
            description false
    }
    element "Vocation Document Store" {
            shape Cylinder
            background #F7F7F5
            color #1F2933
            stroke #4B5563
            strokeWidth 1
            description false
    }
    relationship "Vocation Internal" {
            color #6B7280
            thickness 1
            fontSize 15
    }
}
