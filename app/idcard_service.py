"""
Professional ID Card Service for TechXelarate Hackathon.
Generates and manages high-quality ID cards with QR codes and team branding.
"""

import os
import logging
import json
import qrcode
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from .quotes import get_random_quote
from .config import settings

logger = logging.getLogger(__name__)


class IDCardService:
    """Service for generating professional hackathon ID cards."""
    
    def __init__(self, output_dir: str = None):
        """
        Initialize ID Card Service.
        
        Args:
            output_dir: Directory to save generated PDFs (default: settings.ASSETS_DIR)
        """
        self.output_dir = output_dir or settings.ASSETS_DIR
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Card dimensions (vertical badge 3.5" x 5.5" @ 300 DPI)
        self.card_width_px = 1050
        self.card_height_px = 1650
        self.dpi = 300
        
        logger.info(f"✓ IDCardService initialized, output_dir: {self.output_dir}")
    
    def generate_qr_code(self, data: Dict, size: int = 200) -> Image.Image:
        """
        Generate QR code from attendance data.
        
        Args:
            data: Dictionary with team_id, access_key, timestamp (QR payload)
            size: QR code size in pixels
            
            Returns:
            PIL Image object of QR code
        """
        try:
            qr_text = json.dumps(data, separators=(',', ':'))
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=2,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
            
            logger.debug(f"✓ QR code generated for participant: {data.get('participant_id')}")
            return qr_img
        except Exception as e:
            logger.error(f"❌ Failed to generate QR code: {e}")
            raise
    
    def create_card_image(
        self,
        team_data: Dict,
        member_data: Dict,
        member_index: int
    ) -> Image.Image:
        """
        Create a single ID card as a PIL Image.
        
        Args:
            team_data: Team information (team_id, team_name, domain, access_key, etc.)
            member_data: Member information (name, email, photo_path, participant_id, etc.)
            member_index: Index of member in team
            
        Returns:
            PIL Image object
        """
        try:
            # Create blank card with dark background
            card = Image.new(
                'RGB',
                (self.card_width_px, self.card_height_px),
                color=(10, 14, 39)  # Dark navy blue
            )
            draw = ImageDraw.Draw(card)
            
            # Try to load fonts, fallback to default if not available
            try:
                header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
                info_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
                small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
                quote_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 18)
            except (OSError, IOError):
                # Fallback to default font on Windows/other systems
                header_font = ImageFont.load_default()
                title_font = ImageFont.load_default()
                name_font = ImageFont.load_default()
                info_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
                quote_font = ImageFont.load_default()
            
            # --- HEADER SECTION ---
            # College name and branding
            y_pos = 40
            draw.text((525, y_pos), "LBRCE", fill=(0, 255, 136), font=header_font, anchor="mm")  # Neon green
            y_pos += 45
            draw.text((525, y_pos), "Hackathon 2026", fill=(0, 232, 255), font=info_font, anchor="mm")  # Neon cyan
            
            # --- PHOTO SECTION ---
            y_pos += 80
            photo_y = y_pos
            photo_size = 280
            
            # Try to load member photo
            if member_data.get('photo_path') and os.path.exists(member_data['photo_path']):
                try:
                    photo = Image.open(member_data['photo_path'])
                    photo = photo.convert('RGB')
                    # Resize to fit circular frame
                    photo = photo.resize((photo_size, photo_size), Image.Resampling.LANCZOS)
                    
                    # Create circular mask
                    mask = Image.new('L', (photo_size, photo_size), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse([0, 0, photo_size, photo_size], fill=255)
                    
                    # Apply circular mask
                    photo.putalpha(mask)
                    card.paste(photo, (int(525 - photo_size/2), photo_y), photo)
                    logger.debug(f"✓ Photo loaded for member {member_index}")
                except Exception as e:
                    logger.warning(f"Could not load photo: {e}")
                    # Draw placeholder circle
                    circle_x = 525 - photo_size//2
                    draw.ellipse(
                        [circle_x, photo_y, circle_x + photo_size, photo_y + photo_size],
                        outline=(0, 232, 255),
                        width=3
                    )
            else:
                # Draw placeholder circle
                circle_x = 525 - photo_size//2
                draw.ellipse(
                    [circle_x, photo_y, circle_x + photo_size, photo_y + photo_size],
                    outline=(0, 232, 255),
                    width=3
                )
            
            # --- MAIN TITLE ---
            y_pos = photo_y + photo_size + 40
            draw.text((525, y_pos), "TechXelarate", fill=(200, 0, 255), font=title_font, anchor="mm")  # Neon magenta
            y_pos += 60
            draw.text((525, y_pos), "6-HOUR HACKATHON", fill=(255, 170, 0), font=info_font, anchor="mm")  # Neon orange
            
            # --- MEMBER INFO SECTION ---
            y_pos += 80

            # Team ID
            draw.text((525, y_pos), f"Team ID: {team_data.get('team_id', 'N/A')}", 
                     fill=(255, 255, 0), font=small_font, anchor="mm")  # Yellow

            y_pos += 50
            
            # Member name
            member_name = member_data.get('name', 'Unknown')
            draw.text((525, y_pos), member_name, fill=(0, 255, 136), font=name_font, anchor="mm")  # Neon green
            
            y_pos += 60
            
            # Team name
            draw.text((525, y_pos), f"Team: {team_data.get('team_name', 'N/A')}", 
                     fill=(0, 232, 255), font=info_font, anchor="mm")  # Cyan
            
            y_pos += 50
            
            # Participant ID
            participant_id = member_data.get('participant_id', f"TEMP-{member_index:03d}")
            draw.rectangle(
                [50, y_pos - 20, 1000, y_pos + 30],
                outline=(200, 0, 255),
                width=2
            )
            draw.text((525, y_pos + 5), participant_id, fill=(255, 255, 255), font=info_font, anchor="mm")
            
            y_pos += 70
            
            # Domain/Track
            draw.text((525, y_pos), f"Track: {team_data.get('domain', 'General')}", 
                     fill=(200, 0, 255), font=small_font, anchor="mm")  # Magenta
            
            y_pos += 50
            
            # Year
            draw.text((525, y_pos), f"Year: {team_data.get('year', 'N/A')}", 
                     fill=(0, 255, 136), font=small_font, anchor="mm")  # Green
            
            # --- QR CODE SECTION ---
            y_pos += 80
            
            # Generate QR code (contains only team_id + access_key)
            qr_data = {
                "team_id": team_data.get('team_id'),
                "access_key": team_data.get('access_key')
            }
            qr_img = self.generate_qr_code(qr_data, size=180)
            
            # Paste QR code centered
            qr_x = 525 - 90
            card.paste(qr_img, (qr_x, y_pos))
            
            y_pos += 200
            
            # Participant ID under QR
            draw.text((525, y_pos), participant_id, fill=(255, 170, 0), font=small_font, anchor="mm")
            
            # --- MOTIVATIONAL QUOTE ---
            y_pos += 50
            quote = get_random_quote()
            
            # Word wrap quote to fit width
            words = quote.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 45:  # Approximate character width
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw quote lines
            for line in lines:
                draw.text((525, y_pos), f'"{line}"', fill=(170, 170, 255), font=quote_font, anchor="mm")
                y_pos += 30
            
            logger.info(f"✓ Card image created for member {member_index}: {member_name}")
            return card
            
        except Exception as e:
            logger.error(f"❌ Failed to create card image: {e}")
            raise
    
    def generate_pdf(
        self,
        team_data: Dict,
        team_members: List[Dict],
        output_filename: str = None
    ) -> str:
        """
        Generate PDF with ID cards for all team members.
        
        Args:
            team_data: Team information
            team_members: List of member dictionaries
            output_filename: Name of output PDF
            
        Returns:
            Path to generated PDF file
        """
        if not output_filename:
            team_id = team_data.get('team_id', 'team')
            output_filename = f"{team_id}_id_cards.pdf"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            logger.info(f"📄 Generating ID cards PDF: {output_filename}")
            
            # Create PDF canvas
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter
            
            # Process each team member
            for idx, member in enumerate(team_members):
                try:
                    logger.info(f"  Processing member {idx + 1}/{len(team_members)}: {member.get('name', 'Unknown')}")
                    
                    # Create card image
                    card_img = self.create_card_image(team_data, member, idx)
                    
                    # Save card image temporarily
                    temp_img_path = os.path.join(self.output_dir, f"temp_card_{idx}.png")
                    card_img.save(temp_img_path, 'PNG')
                    
                    # Convert to fit on letter-size page
                    # Scale down to fit on page
                    img_in_inches = self.card_width_px / self.dpi, self.card_height_px / self.dpi
                    x = (width - img_in_inches[0] * inch) / 2
                    y = (height - img_in_inches[1] * inch) / 2
                    
                    c.drawImage(
                        temp_img_path,
                        x, y,
                        width=img_in_inches[0] * inch,
                        height=img_in_inches[1] * inch
                    )
                    
                    c.showPage()
                    
                    # Clean up temp image
                    try:
                        os.remove(temp_img_path)
                    except:
                        pass
                    
                    logger.debug(f"✓ Member {idx + 1} card added to PDF")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing member {idx}: {e}")
                    continue
            
            # Save PDF
            c.save()
            
            logger.info(f"✅ ID cards PDF generated successfully: {output_path}")
            logger.info(f"   Total members: {len(team_members)} cards generated")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Failed to generate PDF: {e}")
            raise
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary image files."""
        try:
            import glob
            for temp_file in glob.glob(os.path.join(self.output_dir, "temp_*.png")):
                os.remove(temp_file)
                logger.debug(f"Cleaned up: {temp_file}")
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {e}")
