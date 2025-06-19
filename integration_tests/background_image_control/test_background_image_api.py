#!/usr/bin/env python3
"""Integration tests for background image generation and control endpoints."""

import asyncio
import json
import os
import time

import requests
import websockets

# Test configuration
API_BASE = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"
FRONTEND_BACKGROUND_DIR = "prototype/frontend/public/background_pictures"

# Endpoints
GENERATE_ENDPOINT = f"{API_BASE}/api/generate-background-image"
SET_ENDPOINT = f"{API_BASE}/api/set-background-image"
DISABLE_ENDPOINT = f"{API_BASE}/api/disable-background-image"


def test_generate_background_image():
    """Test background image generation API."""
    print("🧪 Testing background image generation...")
    
    payload = {
        "description": "Abstract geometric patterns with vibrant colors",
        "aspect_ratio": "16:9"
    }
    
    response = requests.post(GENERATE_ENDPOINT, json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data.get("success") is True
    assert "filename" in data
    assert "caption" in data
    assert data.get("aspect_ratio") == "16:9"
    
    # Check if file was created in frontend directory
    filename = data["filename"]
    frontend_path = os.path.join(FRONTEND_BACKGROUND_DIR, filename)
    assert os.path.exists(frontend_path), f"Background image not found at {frontend_path}"
    
    print(f"✅ Background image generated: {filename}")
    return filename


def test_set_existing_background():
    """Test setting existing background image."""
    print("🧪 Testing setting existing background...")
    
    # Test with predefined background
    payload = {"filename": "outerspace1.png"}
    
    response = requests.post(SET_ENDPOINT, json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data.get("success") is True
    assert data.get("filename") == "outerspace1.png"
    
    print("✅ Successfully set existing background")


def test_set_nonexistent_background():
    """Test setting non-existent background image."""
    print("🧪 Testing setting non-existent background...")
    
    payload = {"filename": "nonexistent_background.png"}
    
    response = requests.post(SET_ENDPOINT, json=payload)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    
    print("✅ Correctly returned 404 for non-existent background")


def test_disable_background():
    """Test disabling background image."""
    print("🧪 Testing background disable...")
    
    response = requests.post(DISABLE_ENDPOINT)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data.get("success") is True
    
    print("✅ Successfully disabled background")


async def test_websocket_background_generated():
    """Test WebSocket notification for background generation."""
    print("🧪 Testing WebSocket notification for background generation...")
    
    async with websockets.connect(WS_URL) as ws:
        # Generate background image
        payload = {
            "description": "Futuristic neon cityscape at night",
            "aspect_ratio": "16:9"
        }
        requests.post(GENERATE_ENDPOINT, json=payload)
        
        # Wait for WebSocket message
        message = await asyncio.wait_for(ws.recv(), timeout=15)
        data = json.loads(message)
        
        assert data.get("type") == "background-image-generated"
        assert "filename" in data
        assert "caption" in data
        assert data.get("aspect_ratio") == "16:9"
        assert "timestamp" in data
        
        print(f"✅ Received WebSocket notification: {data['filename']}")
        return data["filename"]


async def test_websocket_background_changed():
    """Test WebSocket notification for background change."""
    print("🧪 Testing WebSocket notification for background change...")
    
    async with websockets.connect(WS_URL) as ws:
        # Set background image
        payload = {"filename": "outerspace2.png"}
        requests.post(SET_ENDPOINT, json=payload)
        
        # Wait for WebSocket message
        message = await asyncio.wait_for(ws.recv(), timeout=10)
        data = json.loads(message)
        
        assert data.get("type") == "background-image-changed"
        assert data.get("filename") == "outerspace2.png"
        assert data.get("enabled") is True
        assert "timestamp" in data
        
        print("✅ Received WebSocket notification for background change")


async def test_websocket_background_disabled():
    """Test WebSocket notification for background disable."""
    print("🧪 Testing WebSocket notification for background disable...")
    
    async with websockets.connect(WS_URL) as ws:
        # Disable background
        requests.post(DISABLE_ENDPOINT)
        
        # Wait for WebSocket message
        message = await asyncio.wait_for(ws.recv(), timeout=10)
        data = json.loads(message)
        
        assert data.get("type") == "background-image-changed"
        assert data.get("filename") is None
        assert data.get("enabled") is False
        assert "timestamp" in data
        
        print("✅ Received WebSocket notification for background disable")


def test_missing_parameters():
    """Test API error handling for missing parameters."""
    print("🧪 Testing missing parameters...")
    
    # Test generate-background-image without description
    response = requests.post(GENERATE_ENDPOINT, json={"aspect_ratio": "16:9"})
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"
    
    # Test set-background-image without filename
    response = requests.post(SET_ENDPOINT, json={})
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    
    print("✅ Correctly handled missing parameters")


async def run_all_tests():
    """Run all tests in sequence."""
    print("🚀 Starting background image control integration tests...")
    print()
    
    # Basic API tests
    generated_filename = test_generate_background_image()
    test_set_existing_background()
    test_set_nonexistent_background()
    test_disable_background()
    test_missing_parameters()
    
    print()
    print("📡 Testing WebSocket functionality...")
    
    # WebSocket tests
    ws_generated_filename = await test_websocket_background_generated()
    await test_websocket_background_changed()
    await test_websocket_background_disabled()
    
    print()
    print("🧹 Testing with generated background...")
    
    # Test with generated background
    if generated_filename:
        payload = {"filename": generated_filename}
        response = requests.post(SET_ENDPOINT, json=payload)
        assert response.status_code == 200
        print(f"✅ Successfully set generated background: {generated_filename}")
    
    print()
    print("🎉 All background image control tests passed!")
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"   Generated backgrounds: {generated_filename}, {ws_generated_filename}")
    print(f"   Predefined backgrounds tested: outerspace1.png, outerspace2.png")
    print(f"   API endpoints tested: 3")
    print(f"   WebSocket events tested: 3")
    print(f"   Error conditions tested: 2")


if __name__ == "__main__":
    # Run tests
    asyncio.run(run_all_tests()) 