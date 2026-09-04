# Face Verification Pipeline

This repository contains the microservices for the HH Goa 2026 Shortlisting Task 3: Face Identification & Blockchain Verification.

## Project Structure

The project is divided into distinct modules, allowing different teams to work independently.

### `blockchain/`
Handles the content provenance and verification. It receives discovered social media data, generates a canonical hash, and uploads it to the Ethereum testnet via a smart contract. See `blockchain/README.md` for specific setup instructions for the junior developer.

### `ml_pipeline/`
Handles the face detection and recognition logic. Takes an input image and extracts face encodings.

### `search_engine/`
Takes the face encodings and searches the web/social media to find genuine matching posts. Returns the discovered post metadata to the blockchain module.

### `shared/`
Contains shared utilities, constants, and data models used across multiple modules to ensure smooth integration.
