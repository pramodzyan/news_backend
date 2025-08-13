from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import io
import os


def optimize_image(image_field, max_width=1200, max_height=800, quality=85):
    """
    Optimize uploaded images by resizing and compressing them
    """
    if not image_field:
        return None
    
    try:
        # Open the image
        image = Image.open(image_field)
        
        # Convert RGBA to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Auto-orient the image based on EXIF data
        image = ImageOps.exif_transpose(image)
        
        # Calculate new dimensions while maintaining aspect ratio
        width, height = image.size
        if width > max_width or height > max_height:
            # Calculate the scaling factor
            scale_factor = min(max_width / width, max_height / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            # Resize the image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save the optimized image
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Create a new ContentFile
        optimized_image = ContentFile(output.read())
        
        # Generate a new filename
        original_name = os.path.splitext(image_field.name)[0]
        optimized_name = f"{original_name}_optimized.jpg"
        
        return optimized_name, optimized_image
        
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return None


def create_thumbnail(image_field, size=(300, 200)):
    """
    Create a thumbnail version of the image
    """
    if not image_field:
        return None
    
    try:
        # Open the image
        image = Image.open(image_field)
        
        # Convert RGBA to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Auto-orient the image
        image = ImageOps.exif_transpose(image)
        
        # Create thumbnail
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save the thumbnail
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=90, optimize=True)
        output.seek(0)
        
        # Create a new ContentFile
        thumbnail = ContentFile(output.read())
        
        # Generate thumbnail filename
        original_name = os.path.splitext(image_field.name)[0]
        thumbnail_name = f"{original_name}_thumb.jpg"
        
        return thumbnail_name, thumbnail
        
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return None


def get_upload_path(instance, filename):
    """
    Generate upload path based on model and date
    """
    from django.utils import timezone
    
    # Get the model name
    model_name = instance.__class__.__name__.lower()
    
    # Get current date
    now = timezone.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    
    # Clean filename
    name, ext = os.path.splitext(filename)
    clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_name = clean_name.replace(' ', '_')
    
    return f"{model_name}s/{year}/{month}/{clean_name}{ext}"


def validate_image_size(image, max_size_mb=5):
    """
    Validate image file size
    """
    if image.size > max_size_mb * 1024 * 1024:
        raise ValueError(f"Image file too large. Maximum size is {max_size_mb}MB.")
    return True


def get_image_dimensions(image_field):
    """
    Get image dimensions
    """
    if not image_field:
        return None, None
    
    try:
        with Image.open(image_field) as img:
            return img.size
    except Exception:
        return None, None
