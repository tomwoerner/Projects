# Python (FastAPI route example)
#@app.post("/segment")
#def segment_image(file: UploadFile):
#    image = Image.open(file.file)
#    mask = run_u2net(image)  # Output: binary/alpha mask
#    return mask


from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import torch
import numpy as np
from PIL import Image
import io
import uuid
import os
from pathlib import Path

# Create necessary directories
UPLOAD_DIR = Path("uploads")
MASK_DIR = Path("masks")
UPLOAD_DIR.mkdir(exist_ok=True)
MASK_DIR.mkdir(exist_ok=True)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for serving the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Import U2Net model (install with pip install u2net)
try:
    from u2net import detect as u2net_detect
    
    def run_u2net(image):
        """Run U2Net segmentation on input image"""
        # Convert PIL image to the format expected by U2Net
        img_array = np.array(image)
        
        # Process with U2Net
        mask = u2net_detect.predict(img_array)
        
        # Convert to binary mask if needed
        # Threshold can be adjusted
        binary_mask = (mask > 0.5).astype(np.uint8) * 255
        return Image.fromarray(binary_mask)
        
except ImportError:
    # Fallback for development/testing without U2Net
    def run_u2net(image):
        """Mock U2Net function that creates a simple mask for testing"""
        print("Using mock segmentation (U2Net not installed)")
        # Create a simple oval mask for demonstration
        mask = Image.new('L', image.size, 0)
        width, height = image.size
        center_x, center_y = width // 2, height // 2
        radius_x, radius_y = width // 3, height // 3
        
        # Draw an oval in the center
        for y in range(height):
            for x in range(width):
                # Calculate if point is in oval
                if ((x - center_x) / radius_x) ** 2 + ((y - center_y) / radius_y) ** 2 <= 1:
                    mask.putpixel((x, y), 255)
        
        return mask

@app.get("/")
def read_root():
    """Serve the main page"""
    return FileResponse("static/index.html")

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Process uploaded image and generate a mask"""
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique ID for this session
    session_id = str(uuid.uuid4())
    
    # Read and save original image
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))
    
    # Save original image
    image_path = UPLOAD_DIR / f"{session_id}.png"
    image.save(image_path)
    
    # Generate mask with U2Net
    mask = run_u2net(image)
    
    # Save mask
    mask_path = MASK_DIR / f"{session_id}.png"
    mask.save(mask_path)
    
    return {
        "session_id": session_id,
        "original_url": f"/images/{session_id}.png",
        "mask_url": f"/masks/{session_id}.png"
    }

@app.get("/images/{image_id}.png")
async def get_image(image_id: str):
    """Retrieve original image"""
    image_path = UPLOAD_DIR / f"{image_id}.png"
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

@app.get("/masks/{mask_id}.png")
async def get_mask(mask_id: str):
    """Retrieve mask image"""
    mask_path = MASK_DIR / f"{mask_id}.png"
    if not mask_path.exists():
        raise HTTPException(status_code=404, detail="Mask not found")
    return FileResponse(mask_path)

@app.put("/masks/{mask_id}.png")
async def update_mask(mask_id: str, file: UploadFile = File(...)):
    """Update an existing mask (from manual edits)"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read and save updated mask
    mask_data = await file.read()
    mask_path = MASK_DIR / f"{mask_id}.png"
    
    with open(mask_path, "wb") as f:
        f.write(mask_data)
    
    return {"status": "success", "mask_url": f"/masks/{mask_id}.png"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)