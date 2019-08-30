# Live-AV-Template
A Touchdesigner template for live A/V performance. It is based on the performance system I built for ARIADNE.

This is currently a work in progress but is fully functional.

## Overview

The top level consists of several “modes” (perform, pre-show, post-show, etc) that can be selected for output on the main out node. Switching from one mode to another initiates a fade-out of the current mode to a fade-in of the new mode. The perform mode contains several scenes that can be switched between in a similar fashion. There is also a control node with a UI for the system and a general data “IO” node.

The system control logic is a python api via extensions which can be controlled by custom parameters or the control UI. The control UI can run in a separate TD instance on the same machine or any machine on the local network. 

### Out
  Controls which mode is displayed. Nodes on the same network level that have “MODE” tags are available for selection. All mode changes fade in and out from black. To change modes, chose a mode from the "Set Mode Goal" drop down menu.

### Perform - MODE
  Controls which scenes are displayed. Scenes should be based on the template scenes in the perform mode COMP and must have a tag named "SCENE" to be available for selection. To change the scene, select the desired scene index from the next scene parameter and then click the "Change Scene" parameter button.

### PreShow/PostShow - MODE
  Generic modes for displaying preShow and postShow content. These are a simple version of the perform mode with only a single scene. Fade-in and fade-out times of these modes can be adjusted via their corresponding custom parameters.
  
### Calibrate - MODE
  A mode which displays a calibration grid and enables corner pin calibration which will be applied to all modes. Corner pins can be adjusted via their corresponding custom parameters. The reset parameter will reset all corner pins.
  
### Controls
  A UI for controlling the performance system. It can run in a separate TD instance on the same machine or on a separate machine connected to the local network. The controls node contains UI for the out node, perform node and calibration node. The UI state is updated in realtime via UDP multicast.
  
### IO
  A node which contains all ingoing and outgoing data. Inside this node there is a "base_com" node for controlling UDP multicast communication with the controls node and the audio node which handles audio input and analysis.
