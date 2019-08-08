# Live-AV-Template
A Touchdesigner template for live A/V performance. It is based on the performance system I built for ARIADNE. 

This is currently a work in progress but is fully functional.

## Overview

The top level consists of several “Modes” (perform, pre-show, post-show,etc) that can be selected for output on the main Out node. Switching from one mode to another initiates a fade out of the current mode to a fade in of the new mode. The perform mode contains several scenes that can be switched between in a similar fashion. There is also a Control node with a UI for the system and a general data “IO” node.

The system control is all based a python api via extensions which can be controlled via node custom parameters or the Control UI. The Control UI can run in a separate TD instance on the same machine or any machine on the local network. 

### Out
  Controls which Mode is displayed. Nodes on the same network level that have “MODE” tags are available for selection. 

### Perform - MODE

