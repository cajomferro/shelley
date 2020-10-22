```text

    device DeskLamp:
      actions:
        update_battery_read
      events: 
       level1, level2, standby, batteryRead
      behaviour:
        begin -> level1
        level1 -> standby or level2
        level2 -> standby
        standby -> level1
      devices:
        Led ledA, ledB
        Timer t
        Button b
      triggers:
        level1 <- b.pressed; b.released; ledA.on; t.started
        level2 <- b.pressed; b.released; (t.canceled and ledB.on); t.started
        standby <- ((b.pressed; b.released; t.canceled) or t.timeout); (ledB.off and ledA.off)

```