# NetworkTables-HID

A sketchy work-in-progress way to use HID devices through [NetworkTables](https://docs.wpilib.org/en/stable/docs/software/networktables/networktables-intro.html), a publish-subscribe network protocol used in FRC. This was essentially only made to control our robot with a DDR dance pad for fun, but could probably be useful for other demos and fun projects.

`NTEmulatedCommandXboxController` includes a class that extends from `CommandXboxController` to work as a drop-in replacement for an existing CommandXboxController. It uses NetworkTables to get the controller input instead of directly reading from the controller. There's likely a better way to do this, but this works for now.