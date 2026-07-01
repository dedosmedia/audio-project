# CLAUDE.md

# Audio Project

This repository contains a long-term software project.

The goal is to build a professional network audio intercom.

This is NOT an experiment.
This is NOT a prototype.
The architecture is more important than writing code quickly.

Always prioritize maintainability over writing fewer lines of code.

-------------------------------------------------------------------------------
## Primary Goal

The system must transmit live voice from a Linux Mint PC to a Raspberry Pi over the local network.

Linux Mint
↓

USB microphone

↓

Python application

↓

GStreamer

↓

Opus

↓

RTP/UDP

↓

WiFi

↓

Raspberry Pi

↓

Python application

↓

GStreamer

↓

3.5 mm audio output

↓

Powered speakers

Latency target:

50-100 milliseconds.

-------------------------------------------------------------------------------
## Hardware

### Sender

OS:
Linux Mint

Audio:

USB Fifine microphone

Audio backend:

PipeWire

Python:

3.11+

### Receiver

Raspberry Pi 3

Raspberry Pi OS (Trixie)

Audio output:

hw:1,0

Connected speakers.

-------------------------------------------------------------------------------
## Repository Layout

audio-project/

    pyproject.toml

    README.md

    src/

        intercom/

            shared/

            receiver/

            sender/

    config/

    tests/

    docs/

    service/

-------------------------------------------------------------------------------
## Python Package Layout

src/intercom/

    shared/

        config.py

        logger.py

        constants.py

        exceptions.py

        service.py

        models/

    receiver/

        main.py

        audio/

        api/

    sender/

        main.py

        audio/

        input/

-------------------------------------------------------------------------------
## Architecture Principles

Always keep responsibilities separated.

The receiver should know NOTHING about:

- FastAPI
- HTTP
- Home Assistant
- MQTT
- Flutter

The receiver only manages audio.

The sender only captures and sends audio.

REST belongs to another layer.

-------------------------------------------------------------------------------
## Audio Backend

Use GStreamer.

Avoid Gst.parse_launch() for production code.

Instead create pipelines manually using:

Gst.Pipeline()

Gst.ElementFactory.make()

Reason:

We need dynamic control over:

- reconnect
- bitrate
- output device
- DSP
- AGC
- equalizer
- recording
- diagnostics

Every element should be stored as an instance variable.

-------------------------------------------------------------------------------
## Transport

Use:

Opus

RTP

UDP

Never TCP.

-------------------------------------------------------------------------------
## Future REST API

Receiver will expose:

GET /status

POST /volume

POST /mute

POST /start

POST /stop

The REST layer must call the receiver.

The receiver must never import FastAPI.

-------------------------------------------------------------------------------
## Service Architecture

Every long-running component must inherit from:

Service

Interface:

start()

stop()

restart()

is_running()

-------------------------------------------------------------------------------
## Logging

Never use print().

Always use logging.

Future logs:

logs/

receiver.log

sender.log

Log format:

timestamp

level

module

message

-------------------------------------------------------------------------------
## Configuration

Never hardcode values.

Load configuration from YAML.

Example:

receiver.yaml

audio:

    device: hw:1,0

    latency_ms: 20

network:

    udp_port: 5002

volume:

    default: 0.5

-------------------------------------------------------------------------------
## Error Handling

Never swallow exceptions.

Create custom exception classes.

Recover automatically whenever possible.

-------------------------------------------------------------------------------
## Bus Monitoring

Always monitor Gst.Bus.

Handle:

ERROR

WARNING

EOS

STATE_CHANGED

Automatically report pipeline status.

-------------------------------------------------------------------------------
## Dependency Injection

Prefer dependency injection.

Avoid constructing dependencies inside business classes.

Example:

pipeline = GstAudioPipeline(config)

receiver = Receiver(pipeline)

Instead of:

receiver = Receiver(config)

-------------------------------------------------------------------------------
## Future Features

Push-To-Talk

Voice Activity Detection

REST control

Home Assistant integration

Flutter Web dashboard

Multi-room support

Bidirectional audio

DSP

Automatic reconnect

-------------------------------------------------------------------------------
## Coding Standards

Everything in code must be English.

Conversation with the user is Spanish.

Variables:

English

Functions:

English

Comments:

English

Documentation:

English

-------------------------------------------------------------------------------
## Python Standards

Python 3.11+

Type hints everywhere.

Dataclasses whenever appropriate.

Avoid global variables.

Avoid singleton patterns unless justified.

Document public APIs.

-------------------------------------------------------------------------------
## Testing

Write tests whenever a module does not depend on hardware.

Configuration

Models

Logger

Service lifecycle

Utilities

Protocol

Network

-------------------------------------------------------------------------------
## Refactoring Rules

Before introducing a new dependency:

Explain why.

Before adding a new abstraction:

Explain why.

Never rewrite unrelated code.

Never perform large refactors unless requested.

Keep commits focused.

-------------------------------------------------------------------------------
## Response Rules

When modifying code:

Always return COMPLETE files.

Never return partial snippets unless explicitly requested.

When proposing architectural changes:

Explain the motivation first.

Keep the project runnable after every change.

-------------------------------------------------------------------------------
## Development Philosophy

This project will evolve over many months.

Always think about:

maintainability

testability

modularity

future extensibility

Prefer a clean architecture over a shorter implementation.

When in doubt, optimize for readability.

The user prefers iterative development where every milestone produces a working application.

Always preserve the overall architecture.