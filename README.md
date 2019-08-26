# Live-AV-Template
A Touchdesigner template for live A/V performance. It is based on the performance system I built for ARIADNE. 

This is currently a work in progress but is fully functional.

## Overview

The top level consists of several “Modes” (perform, pre-show, post-show,etc) that can be selected for output on the main Out node. Switching from one mode to another initiates a fade-out of the current mode to a fade-in of the new mode. The perform mode contains several scenes that can be switched between in a similar fashion. There is also a Control node with a UI for the system and a general data “IO” node.

The system control is a python api via extensions which can be controlled by custom parameters or the Control UI. The Control UI can run in a separate TD instance on the same machine or any machine on the local network. 

### Out
  Controls which Mode is displayed. Nodes on the same network level that have “MODE” tags are available for selection. All mode changes fade in and out from black. To change Modes, chose a mode from the "Set Mode Goal" drop down menu.

### Perform - MODE
  Controls which scenes are displayed. Scenes should be based on the template scenes in the Perform mode COMP and must have a tag named "SCENE" to be available for selection. To change the scene, select the scene index from the next scene parameter and then click the "Change Scene" parameter button.

### PreShow/PostShow - MODE
  Generaic modes for displaying preShow and postShow content. These are a simple version of the perform mode with only a single scene. Fade-in and fade-out times of these modes can be adjusted via their corresponding custom parameters.
  
### Calibrate - MODE
  A mode which displays a calibration grid and enables corner pin calibration which will be applied to all modes. Corner pins can be adjusted via their corresponding custom parameters. The reset parameter will reset all corner pins.
  
### Controls
  A UI for controlling the performanc system. Can run in a separate TD instance on the same machine or any machine on the local network. The Controls node contains UI for the Out node, Perform node and Calibration node. The UI state is updated in realtime via UDP multicast.
  
### IO
  A node which contains all ingoing and outgoign data. Inside this node there is a base_com node for controlling UDP multicast communication with the Controls node and and Audio node which handles audio input and analysis.
