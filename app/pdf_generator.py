"""
Professional ID Card Generator for TechXelarate Hackathon.
Generates beautiful, production-ready ID cards with all required elements.

Features:
- Dynamic vertical badge-style ID cards
- Professional futuristic theme with neon aesthetic
- LBRCE college branding
- TechXelarate hackathon branding  
- Holographic-style header design
- Participant photo with premium borders
- Unique centered Hackathon ID
- Random motivational quote per participant
- High-resolution PDF export
"""

import os
import logging
# the QR library has been removed; ID cards no longer include codes
from io import BytesIO
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, mm, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Spacer, PageBreak
from PIL import Image as PILImage, ImageDraw, ImageFont, ImageFilter
from .quotes import get_random_quote

logger = logging.getLogger(__name__)


class IDCardGenerator:
    """Generate premium ID cards for hackathon participants."""
    
    def __init__(self, output_dir: str = "assets"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Card dimensions - vertical badge style (3.5" x 5.5")
        self.card_width_px = 1050   # 3.5" @ 300 DPI
        self.card_height_px = 1650  # 5.5" @ 300 DPI
        self.dpi = 300
    
    def generate_participant_id_cards(
        self,
        team_data: dict,
        team_members_list: list,
        output_filename: str = None
    ) -> str:
        """
        Generate ID cards for all team members in a single PDF.
        
        Args:
            team_data: Dictionary with team_id, team_name, domain, year, access_key, etc.
            team_members_list: List of dicts with {name, email, photo_path, participant_id}
           output_filename: Name of output PDF file
            
        Returns:
            Path to generated PDF file
        """
        if not output_filename:
            output_filename = f"{team_data.get('team_id', 'team')}_id_cards.pdf"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # Generate card images
            card_images = []
            card_img_paths = []
            
            for idx, member in enumerate(team_members_list):
                # Generate card image
                card_img_path = self._create_premium_id_card(team_data, member, idx)
                
                if card_img_path and os.path.exists(card_img_path):
                    try:
                        # Load image
                        img = PILImage.open(card_img_path)
                        # Convert RGBA to RGB if necessary (for PDF compatibility)
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        card_images.append(img)
                        card_img_paths.append(card_img_path)
                        logger.debug(f"✅ Loaded card image {idx}: {card_img_path}")
                    except Exception as e:
                        logger.error(f"Error loading card image {idx}: {e}")
                else:
                    logger.warning(f"Failed to generate card image for member {idx}")
            
            if not card_images:
                logger.error("No card images were created!")
                raise ValueError("PDF generation failed: no cards created")
            
            # Save all images to PDF using PIL
            abs_output_path = os.path.abspath(output_path)
            logger.info(f"📝 Saving {len(card_images)} cards to PDF: {abs_output_path}")
            
            # Use PIL to save images as PDF
            card_images[0].save(
                abs_output_path,
                'PDF',
                save_all=True,
                append_images=card_images[1:] if len(card_images) > 1 else []
            )
            
            logger.info(f"✅ ID cards PDF created with {len(card_images)} cards: {abs_output_path}")
            
            # Verify PDF was created
            if not os.path.exists(abs_output_path):
                raise ValueError(f"PDF was not created: {abs_output_path}")
            
            pdf_size = os.path.getsize(abs_output_path)
            if pdf_size < 1000:
                logger.warning(f"⚠️ PDF size very small ({pdf_size} bytes) - may be corrupted!")
            else:
                logger.info(f"✅ PDF size: {pdf_size:,} bytes")
            
            return abs_output_path
            
        except Exception as e:
            logger.exception(f"❌ Failed to generate ID cards: {e}")
            raise
    
    def _create_premium_id_card(self, team_data: dict, member: dict, member_idx: int = 0) -> str:
        """
        Create a single premium ID card as PNG image.
        
        Design:
        - Vertical badge format (3.5" x 5.5")
        - Top: LBRCE header with holographic effect
        - Upper: TechXelarate branding
        - Middle: Participant photo with premium frame
        - Lower: Participant info
        - Bottom: decorative status text ("Verified Participant") instead of QR
        """
        try:
            logger.info(f"📱 Generating ID card for {member.get('name', 'Member')}")
            
            # Create base image with gradient background
            img = self._create_gradient_background()
            
            # Draw all elements
            self._draw_header(img, "LBRCE")
            self._draw_subheader(img, "Laki Reddy Bali Reddy College of Engineering")
            self._draw_tech_branding(img)
            self._add_participant_photo(img, member)
            self._draw_participant_info(img, member, team_data)
            self._draw_quote(img, member)
            # Instead of QR we add a status line and decorative bubbles
            self._add_status_section(img)
            
            # Save card image
            output_filename = f"id_card_{team_data.get('team_id', 'unknown')}_{member_idx}.png"
            output_path = os.path.join(self.output_dir, output_filename)
            img.save(output_path, 'PNG', quality=95)
            logger.info(f"✅ Card image saved: {output_path}")
            return output_path
        
        except Exception as e:
            logger.exception(f"❌ Error creating card: {e}")
            return None
    
    def _add_status_section(self, img: PILImage.Image):
        """Draw status text with minimal decorative accents."""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        y_pos = height - 300
        try:
            info_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except Exception:
            info_font = ImageFont.load_default()
        # status text in dark blue
        draw.text((width//2, y_pos), "Verified Participant", fill=(30, 100, 150), font=info_font, anchor="mm")
        # minimal subtle dots instead of bubbles
        import random
        random.seed(42)
        for _ in range(5):
            rx = random.randint(100, width - 100)
            ry = random.randint(y_pos + 50, y_pos + 180)
            rsize = random.randint(8, 20)
            draw.ellipse([rx, ry, rx + rsize, ry + rsize], outline=(180, 210, 240), width=1)
    
    def _create_gradient_background(self) -> PILImage.Image:
        """Create minimal light background with soft gradient from white to light blue."""
        img = PILImage.new('RGB', (self.card_width_px, self.card_height_px))
        draw = ImageDraw.Draw(img)
        # soft white to light blue gradient (top to bottom)
        for y in range(self.card_height_px):
            t = y / self.card_height_px
            # Start: nearly white (245, 248, 250)
            # End: soft light blue (225, 240, 250)
            r = int(245 - t * 20)  
            g = int(248 - t * 8)   
            b = int(250 - t * 0)   
            draw.line([(0, y), (self.card_width_px, y)], fill=(r, g, b))
        
        # minimal accent: subtle light gray lines (not dark)
        import random
        random.seed(42)  # reproducible pattern
        for _ in range(8):
            x1 = random.randint(0, self.card_width_px)
            y1 = random.randint(0, self.card_height_px // 3)
            x2 = random.randint(0, self.card_width_px)
            y2 = random.randint(0, self.card_height_px // 3)
            draw.line([(x1, y1), (x2, y2)], fill=(220, 230, 240), width=1)
        
        return img
    
    def _draw_header(self, img: PILImage.Image, text: str):
        """Draw LBRCE header with soft blue accent."""
        draw = ImageDraw.Draw(img, 'RGBA')
        
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.card_width_px - text_width) // 2
        y = 40
        
        # Main text in dark blue (not bright cyan)
        draw.text((x, y), text, fill=(30, 100, 150, 255), font=font)
    
    def _draw_subheader(self, img: PILImage.Image, text: str):
        """Draw college name subtitle in soft gray."""
        draw = ImageDraw.Draw(img, 'RGBA')
        
        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.card_width_px - text_width) // 2
        
        # Soft gray text
        draw.text((x, 110), text, fill=(100, 120, 140, 200), font=font)
        
        # Divider line (light blue)
        draw.line([(80, 145), (self.card_width_px - 80, 145)], 
                 fill=(180, 210, 240, 200), width=2)
    
    def _draw_tech_branding(self, img: PILImage.Image):
        """Draw TechXelarate branding with golden text."""
        draw = ImageDraw.Draw(img, 'RGBA')
        
        try:
            font_main = ImageFont.truetype("arial.ttf", 72)
            font_year = ImageFont.truetype("arial.ttf", 28)
        except:
            font_main = ImageFont.load_default()
            font_year = ImageFont.load_default()
        
        # Main branding
        text = "TechXelarate"
        bbox = draw.textbbox((0, 0), text, font=font_main)
        text_width = bbox[2] - bbox[0]
        x = (self.card_width_px - text_width) // 2
        
        # Glow effect (golden)
        for glow in [6, 4, 2]:
            draw.text((x + glow, 160), text, fill=(255, 200, 50, 100), font=font_main)
        
        # Main text (bright gold)
        draw.text((x, 160), text, fill=(255, 230, 0, 255), font=font_main)
        
        # Year/Event
        year_text = "2026 HACKATHON"
        bbox_year = draw.textbbox((0, 0), year_text, font=font_year)
        year_width = bbox_year[2] - bbox_year[0]
        x_year = (self.card_width_px - year_width) // 2
        draw.text((x_year, 250), year_text, fill=(200, 220, 255, 200), font=font_year)
    
    def _add_participant_photo(self, img: PILImage.Image, member: dict):
        """Add circular participant photo with premium border."""
        try:
            photo_size = 300
            photo_x = (self.card_width_px - photo_size) // 2
            photo_y = 320
            
            # Load or create placeholder photo
            photo_path = member.get('photo_path')
            if photo_path and os.path.exists(photo_path):
                try:
                    photo = PILImage.open(photo_path).convert('RGB')
                    photo = photo.resize((photo_size, photo_size), PILImage.Resampling.LANCZOS)
                    logger.info(f"✅ Loaded photo for {member.get('name')}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load photo: {e}, using placeholder")
                    photo = self._create_placeholder_photo(photo_size)
            else:
                logger.info(f"ℹ️ No photo for {member.get('name')}, using placeholder")
                photo = self._create_placeholder_photo(photo_size)
            
            # Create circular mask
            mask = PILImage.new('L', (photo_size, photo_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, photo_size, photo_size), fill=255)
            
            # Apply mask to photo
            photo_rgba = photo.convert('RGBA')
            photo_rgba.putalpha(mask)
            img.paste(photo_rgba, (photo_x, photo_y), photo_rgba)
            
            # Add decorative border rings
            draw = ImageDraw.Draw(img, 'RGBA')
            
            # Outer cyan ring
            draw.ellipse(
                [(photo_x - 10, photo_y - 10), (photo_x + photo_size + 10, photo_y + photo_size + 10)],
                outline=(0, 200, 255, 220),
                width=4
            )
            
            # Middle purple ring
            draw.ellipse(
                [(photo_x - 15, photo_y - 15), (photo_x + photo_size + 15, photo_y + photo_size + 15)],
                outline=(200, 0, 255, 150),
                width=2
            )
            
            logger.info(f"✅ Added photo for {member.get('name')}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to add photo: {e}")
    
    def _create_placeholder_photo(self, size: int) -> PILImage.Image:
        """Create a gradient placeholder when photo is missing."""
        img = PILImage.new('RGB', (size, size), (30, 50, 80))
        draw = ImageDraw.Draw(img)
        
        # Gradient
        for y in range(size):
            ratio = y / size
            color = (
                int(30 + 50 * ratio),
                int(50 + 100 * ratio),
                int(80 + 100 * ratio)
            )
            draw.line([(0, y), (size, y)], fill=color)
        
        # Placeholder text
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        draw.text((size // 2 - 30, size // 2 - 20), "NO", fill=(0, 200, 255), font=font)
        draw.text((size // 2 - 50, size // 2 + 20), "PHOTO", fill=(0, 200, 255), font=font)
        
        return img
    
    def _draw_participant_info(self, img: PILImage.Image, member: dict, team_data: dict):
        """Draw participant information with color-coded fields and team code."""
        draw = ImageDraw.Draw(img, 'RGBA')
        
        try:
            name_font = ImageFont.truetype("arial.ttf", 44)
            info_font = ImageFont.truetype("arial.ttf", 24)
            label_font = ImageFont.truetype("arial.ttf", 16)
            code_font = ImageFont.truetype("arial.ttf", 14)
        except:
            name_font = ImageFont.load_default()
            info_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            code_font = ImageFont.load_default()
        
        y_pos = 650
        
        # Team ID (small, at top)
        team_id_small = team_data.get('team_id', '')
        if team_id_small:
            code_text = f"{team_id_small}"
            bbox = draw.textbbox((0, 0), code_text, font=code_font)
            code_width = bbox[2] - bbox[0]
            x_code = (self.card_width_px - code_width) // 2
            draw.text((x_code, y_pos - 40), code_text, fill=(255, 170, 0, 200), font=code_font)
        
        # Participant Name (prominent, centered, dark blue)
        name = member.get('name', 'Unknown')
        bbox = draw.textbbox((0, 0), name, font=name_font)
        name_width = bbox[2] - bbox[0]
        x = (self.card_width_px - name_width) // 2
        draw.text((x, y_pos), name, fill=(30, 100, 150, 255), font=name_font)
        
        y_pos += 60
        
        # Team Name in soft blue
        team_name = team_data.get('team_name', 'Team')
        bbox = draw.textbbox((0, 0), team_name, font=info_font)
        team_width = bbox[2] - bbox[0]
        x_team = (self.card_width_px - team_width) // 2
        draw.text((x_team, y_pos), f"Team: {team_name}", fill=(80, 130, 180, 200), font=info_font)
        
        y_pos += 45
        
        # Hackathon ID (centered and bold, dark blue)
        team_id = team_data.get('team_id', 'HACK-000')
        bbox = draw.textbbox((0, 0), team_id, font=name_font)
        team_id_width = bbox[2] - bbox[0]
        x_id = (self.card_width_px - team_id_width) // 2
        
        # ID background box with light blue outline
        draw.rectangle(
            [(x_id - 15, y_pos - 5), (x_id + team_id_width + 15, y_pos + 50)],
            outline=(150, 190, 230, 150),
            width=2
        )
        draw.text((x_id, y_pos), team_id, fill=(30, 100, 150, 255), font=name_font)
        
        y_pos += 65
        
        # Domain and Year in soft gray
        domain = team_data.get('domain', 'Domain')
        year = team_data.get('year', 'Year')
        info_text = f"{domain} | {year}"
        bbox = draw.textbbox((0, 0), info_text, font=label_font)
        info_width = bbox[2] - bbox[0]
        x_info = (self.card_width_px - info_width) // 2
        draw.text((x_info, y_pos), info_text, fill=(100, 130, 160, 180), font=label_font)
        
        logger.info(f"✅ Added info for {name}")
    
    def _draw_quote(self, img: PILImage.Image, member: dict):
        """Draw random motivational quote in soft gray."""
        try:
            draw = ImageDraw.Draw(img, 'RGBA')
            
            quote_font = ImageFont.truetype("arial.ttf", 16)
        except:
            quote_font = ImageFont.load_default()
        
        # Get random quote
        quote = get_random_quote()
        
        # Word wrap quote
        max_width = self.card_width_px - 60
        lines = self._wrap_text(quote, quote_font, max_width)
        
        y_pos = 1240
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=quote_font)
            line_width = bbox[2] - bbox[0]
            x = (self.card_width_px - line_width) // 2
            draw.text((x, y_pos), f'"{line}"', fill=(120, 150, 180, 140), font=quote_font)
            y_pos += 25
    
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """Wrap text to fit within max_width."""
        draw = ImageDraw.Draw(PILImage.new('RGB', (1, 1)))
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " " if current_line else word + " "
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines


if __name__ == "__main__":
    # Test
    gen = IDCardGenerator()
    print("✅ ID Card Generator ready")
