# Real-Time RAWS Fuel Moisture Data Quality Classifier

## Overview

This project focuses on quality control for 10-hour fuel moisture observations from Remote Automated Weather Stations (RAWS).
These sensors are used to monitor wildfire risk and inform active fire behavior assessment.
This repository is structured as an agent-driven project: both to explore whether AI agents are well suited to this kind of data-quality workflow, and to demonstrate a concrete use case for agent-based work within wildfire science.

## Background

Many RAWS stations include a 10-hour fuel moisture sensor.
The most common sensor types in these data are Campbell Scientific and Forest Technology Systems.

Station observations are accessed from the Synoptic API using `synopticpy`.
These data include real-time observations from multiple station networks.
The largest network is NIFC RAWS, along with additional stations operated by other public and private organizations, including energy companies.

## Problem

Fuel moisture sensors do not always produce reliable data.
Sensors can break, degrade over time, go offline, or otherwise report poor-quality observations.

These bad observations can contaminate downstream workflows, especially when the data are used for:

- model training
- data assimilation
- model initialization

Ad hoc rules for identifying suspect observations are difficult to maintain and may not generalize well across stations, sensor types, or failure modes.

## Project Goal

The goal of this project is to support development of a classification approach for rapidly flagging suspect fuel moisture data.
The intent is to improve filtering of poor-quality observations before they are used in downstream modeling workflows.

## Setup Notes

To reproduce data-access steps for this project:

1. Create or access a Synoptic account and obtain an API token from the Synoptic website.
2. Copy [etc/tokens.json.initial](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/tokens.json.initial) to `etc/tokens.json`.
3. Replace the placeholder value in `etc/tokens.json` with your Synoptic API token.
