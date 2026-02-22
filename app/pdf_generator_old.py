"""
Premium ID card generator for hackathon participants.
Generates professional event badges with realistic design, participant photos and unique QR codes.

Features:
- Premium gradient background (dark blue → purple)
- Professional LBRCE branding with effects
- TechXelarate event branding
- Large, scannable QR code (unique per participant)
- Circular participant photos with premium borders
- Clear, readable typography
- Unique participant code for attendance check-in
- Professional event badge design with realistic styling
"""
import os
import json
import uuid
import logging
import qrcode
from io import BytesIO
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image as PILImage, ImageDraw, ImageFont
from .quotes import get_random_quote

logger = logging.getLogger(__name__)


class IDCardGenerator:
    """Generate clean, professional ID cards for hackathon participants."""
    
    def __init__(self, output_dir: str = "assets"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Card dimensions - standard ID badge (4x3 inches)
        # Higher resolution for clarity
        self.card_width = 1200  # pixels (4 inches @ 300 DPI)
        self.card_height = 900  # pixels (3 inches @ 300 DPI)
        self.dpi = 300  # High resolution for crisp printing
    
    def generate_participant_id_cards(
        self,
        team_data: dict,
        team_members_list: list,
        output_filename: str = None
    ) -> str:
        """
        Generate ID cards for all team members in a single PDF.
        One card per team member on separate pages.
        
        Args:
            team_data: Dictionary with team_id, access_key, team_name, domain, year, etc.
            team_members_list: List of dicts with {name, email, phone, photo_path}
            output_filename: Name of output PDF file
            
        Returns:
            Path to generated PDF file
        """
        if not output_filename:
            output_filename = f"{team_data.get('team_id', 'team')}_id_cards.pdf"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Create PDF document (landscape letter size for badge print)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(letter),
            rightMargin=0.25*inch,
            leftMargin=0.25*inch,
            topMargin=0.25*inch,
            bottomMargin=0.25*inch
        )
        
        story = []
        
        # Generate one ID card per team member
        for idx, member in enumerate(team_members_list):
            if idx > 0:
                story.append(PageBreak())
            
            # Generate card as image
            card_image_path = self._generate_card_image(
                team_data=team_data,
                member=member,
                member_index=idx
            )
            
            if card_image_path and os.path.exists(card_image_path):
                try:
                    # Add card image to PDF (5.5" x 3.5" landscape badge size)
                    img = Image(card_image_path, width=5.5*inch, height=3.5*inch)
                    story.append(img)
                except Exception as e:
                    # Fallback if image fails
                    print(f"Warning: Failed to add card image: {e}")
                    story.extend(self._create_text_card(team_data, member))
        
        # Build PDF
        try:
            doc.build(story)
            return output_path
        except Exception as e:
            raise Exception(f"Failed to generate ID cards PDF: {str(e)}")
    
    def _generate_card_image(self, team_data: dict, member: dict, member_index: int = 0) -> str:
        """
        Generate a PREMIUM tech conference badge with realistic design.
        
        Design Elements:
        - Professional metallic gradient background
        - Premium LBRCE header with styling
        - TechXelarate branding with visual hierarchy
        - High-quality circular photo with premium gradient border
        - Enhanced typography with professional colors
        - Large scannable QR code with decorative elements
        - Authority badge elements for realistic look
        """
        try:
            # Create stunning gradient background (dark navy to deep purple)
            img = PILImage.new('RGB', (self.card_width, self.card_height), (15, 25, 50))
            draw = ImageDraw.Draw(img, 'RGBA')
            
            # Multi-layer gradient for premium metallic look
            for y in range(self.card_height):
                # Create subtle metallic gradient
                progress = y / self.card_height
                r = int(15 + (50 - 15) * progress)
                g = int(25 + (50 - 25) * progress)
                b = int(50 + (110 - 50) * progress)
                draw.line([(0, y), (self.card_width, y)], fill=(r, g, b))
            
            # Add left accent stripe (cyan to purple gradient)
            stripe_width = 12
            for x in range(stripe_width):
                intensity = int((100 + 155 * (x / stripe_width)))
                r = int(0 + (100 - 0) * (x / stripe_width))
                g = int(200 + (50 - 200) * (x / stripe_width))
                b = int(255 - (0 * (x / stripe_width)))
                draw.line([(x, 0), (x, self.card_height)], fill=(r, g, b))
            
            # Add right accent stripe with glow effect
            for x in range(self.card_width - stripe_width, self.card_width):
                intensity = int(255 * ((self.card_width - x) / stripe_width))
                draw.line([(x, 0), (x, self.card_height)], fill=(0, 180, 255, intensity))
            
            # Get fonts with fallback
            try:
                header_font = ImageFont.truetype("arial.ttf", 44)
                subheader_font = ImageFont.truetype("arial.ttf", 30)
                title_font = ImageFont.truetype("arial.ttf", 68)
                name_font = ImageFont.truetype("arial.ttf", 52)
                info_font = ImageFont.truetype("arial.ttf", 26)
                small_font = ImageFont.truetype("arial.ttf", 19)
                code_font = ImageFont.truetype("arial.ttf", 17)
            except:
                header_font = ImageFont.load_default()
                subheader_font = ImageFont.load_default()
                title_font = ImageFont.load_default()
                name_font = ImageFont.load_default()
                info_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
                code_font = ImageFont.load_default()
            
            # 1. PREMIUM HEADER with enhanced styling
            self._draw_exclusive_header(draw, header_font, subheader_font)
            
            # 2. TECH BRANDING - TechXelarate with premium effects
            self._draw_tech_branding(draw, title_font)
            
            # 3. PROFILE SECTION - Circular photo with premium frame
            self._add_premium_photo_v2(img, member, info_font)
            
            # 4. PARTICIPANT INFO - Professional details with color coding
            self._draw_premium_info_v2(draw, member, name_font, info_font, small_font, code_font)
            
            # 5. QR CODE - Large and scannable with authority badge
            qr_code_img = self._generate_participant_qr_code(team_data, member, member_index)
            self._add_premium_qr_code_v2(img, qr_code_img, member)
            
            # 6. Add event authority badge elements
            self._add_authority_elements(draw, member_index, subheader_font)
            
            # Save as PNG
            output_filename = f"id_card_{team_data.get('team_id', 'unknown')}_{member_index}.png"
            output_path = os.path.join(self.output_dir, output_filename)
            img.save(output_path, 'PNG', quality=95)
            return output_path
        
        except Exception as e:
            logger.error(f"Error generating card image: {str(e)}")
            return None
    
    def _draw_exclusive_header(self, draw, header_font, subheader_font):
        """Draw exclusive LBRCE header with premium effects."""
        # LBRCE Header with glow effect
        title = "LBRCE"
        bbox = draw.textbbox((0, 0), title, font=header_font)
        title_width = bbox[2] - bbox[0]
        x = (self.card_width - title_width) // 2
        
        # Glow effect (multiple layers)
        for glow in range(3, 0, -1):
            draw.text((x + glow, 40), title, fill=(0, 200, 255, 50), font=header_font)
        # Shadow
        draw.text((x + 2, 42), title, fill=(0, 0, 0, 100), font=header_font)
        # Main text - bright cyan
        draw.text((x, 40), title, fill=(0, 255, 255), font=header_font)
        
        # Subtitle with professional styling
        subtitle = "Laki Reddy Bali Reddy College of Engineering"
        bbox_sub = draw.textbbox((0, 0), subtitle, font=subheader_font)
        subtitle_width = bbox_sub[2] - bbox_sub[0]
        x_sub = (self.card_width - subtitle_width) // 2
        draw.text((x_sub, 105), subtitle, fill=(220, 220, 240), font=subheader_font)
        
        # Premium divider with fade effect
        gradient_width = self.card_width - 100
        start_x = 50
        for i in range(4):
            alpha = 255 - (i * 60)
            draw.line([(start_x + i*2, 145), (start_x + gradient_width + i*2, 145)], 
                     fill=(0, 200, 255, alpha), width=2)
    
    def _draw_tech_branding(self, draw, title_font):
        """Draw TechXelarate branding with professional effects."""
        brand = "TechXelarate"
        bbox = draw.textbbox((0, 0), brand, font=title_font)
        brand_width = bbox[2] - bbox[0]
        x = (self.card_width - brand_width) // 2
        
        # Glow effect
        for glow in range(4, 0, -1):
            draw.text((x + glow, 200), brand, fill=(255, 220, 0, 30), font=title_font)
        # Shadow
        draw.text((x + 2, 202), brand, fill=(0, 0, 0, 200), font=title_font)
        # Main text - gold/bright yellow
        draw.text((x, 200), brand, fill=(255, 230, 0), font=title_font)
        
        # Event badge
        try:
            event_font = ImageFont.truetype("arial.ttf", 34)
        except:
            event_font = ImageFont.load_default()
        
        event = "2026 HACKATHON"
        bbox_event = draw.textbbox((0, 0), event, font=event_font)
        event_width = bbox_event[2] - bbox_event[0]
        x_event = (self.card_width - event_width) // 2
        draw.text((x_event, 280), event, fill=(200, 220, 255), font=event_font)
    
    def _add_premium_photo_v2(self, img: PILImage.Image, member: dict, info_font):
        """Add professional circular photo with premium gradient border and ring effects."""
        try:
            photo_size = 240
            photo_x = (self.card_width - photo_size) // 2
            photo_y = 350
            
            # Load and process photo
            if member.get('photo_path') and os.path.exists(member['photo_path']):
                try:
                    photo = PILImage.open(member['photo_path']).convert('RGB')
                    photo = photo.resize((photo_size, photo_size), PILImage.Resampling.LANCZOS)
                except:
                    photo = self._create_placeholder_image(photo_size)
            else:
                photo = self._create_placeholder_image(photo_size)
            
            # Create circular mask with smooth edges
            mask = PILImage.new('L', (photo_size, photo_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, photo_size, photo_size), fill=255)
            
            # Apply mask to photo
            photo_rgba = photo.convert('RGBA')
            photo_rgba.putalpha(mask)
            img.paste(photo_rgba, (photo_x, photo_y), photo_rgba)
            
            # Add premium multi-ring border with gradient
            draw = ImageDraw.Draw(img, 'RGBA')
            
            # Outer glow ring (thick cyan)
            draw.ellipse(
                [(photo_x - 8, photo_y - 8), (photo_x + photo_size + 8, photo_y + photo_size + 8)],
                outline=(0, 200, 255, 200),
                width=4
            )
            
            # Middle ring (purple)
            draw.ellipse(
                [(photo_x - 12, photo_y - 12), (photo_x + photo_size + 12, photo_y + photo_size + 12)],
                outline=(200, 0, 255, 100),
                width=2
            )
            
            # Outer ring (subtle gold)
            draw.ellipse(
                [(photo_x - 15, photo_y - 15), (photo_x + photo_size + 15, photo_y + photo_size + 15)],
                outline=(255, 200, 0, 80),
                width=2
            )
        except Exception as e:
            logger.warning(f"Could not add photo: {e}")
    
    def _draw_premium_info_v2(self, draw, member, name_font, info_font, small_font, code_font):
        """Draw professional participant info with enhanced styling."""
        y_offset = 630
        
        # Participant Name - large and prominent
        name = member.get('name', 'Guest')
        bbox_name = draw.textbbox((0, 0), name, font=name_font)
        name_width = bbox_name[2] - bbox_name[0]
        x_name = (self.card_width - name_width) // 2
        # Shadow
        draw.text((x_name + 2, y_offset + 2), name, fill=(0, 0, 0, 100), font=name_font)
        # Main text - white
        draw.text((x_name, y_offset), name, fill=(255, 255, 255), font=name_font)
        
        y_offset += 70
        
        # Role/Status indicator
        role = "🎖️ EVENT PARTICIPANT" if member.get('is_team_leader') else "👤 PARTICIPANT"
        bbox_role = draw.textbbox((0, 0), role, font=info_font)
        role_width = bbox_role[2] - bbox_role[0]
        x_role = (self.card_width - role_width) // 2
        color = (0, 255, 136) if member.get('is_team_leader') else (0, 200, 255)
        draw.text((x_role, y_offset), role, fill=color, font=info_font)
        
        y_offset += 45
        
        # Participant ID - cyan for emphasis
        participant_id = member.get('participant_id', 'GEN-000000')
        bbox_id = draw.textbbox((0, 0), participant_id, font=code_font)
        id_width = bbox_id[2] - bbox_id[0]
        x_id = (self.card_width - id_width) // 2
        draw.text((x_id, y_offset), participant_id, fill=(0, 255, 200), font=code_font)
    
    def _add_premium_qr_code_v2(self, img: PILImage.Image, qr_code_img: PILImage.Image, member: dict):
        """Add large scannable QR code with professional framing."""
        qr_size = 220
        qr_code_img = qr_code_img.resize((qr_size, qr_size), PILImage.Resampling.LANCZOS)
        
        # Position: bottom right with padding
        qr_x = self.card_width - qr_size - 30
        qr_y = self.card_height - qr_size - 30
        
        # Draw premium QR frame with shadow and glow
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Shadow effect
        draw.rectangle(
            [(qr_x - 12, qr_y - 12), (qr_x + qr_size + 12, qr_y + qr_size + 12)],
            fill=(0, 0, 0, 50)
        )
        
        # Background with gradient border
        draw.rectangle(
            [(qr_x - 10, qr_y - 10), (qr_x + qr_size + 10, qr_y + qr_size + 10)],
            fill=(20, 30, 60, 220),
            outline=(0, 200, 255),
            width=4
        )
        
        # Inner border (purple)
        draw.rectangle(
            [(qr_x - 6, qr_y - 6), (qr_x + qr_size + 6, qr_y + qr_size + 6)],
            outline=(200, 0, 255, 150),
            width=2
        )
        
        # Paste QR code
        img.paste(qr_code_img, (qr_x, qr_y))
        
        # Add corner markers (like professional badges)
        corner_size = 15
        corners = [
            (qr_x - 10, qr_y - 10),  # Top-left
            (qr_x + qr_size, qr_y - 10),  # Top-right
            (qr_x - 10, qr_y + qr_size),  # Bottom-left
            (qr_x + qr_size, qr_y + qr_size)  # Bottom-right
        ]
        for cx, cy in corners:
            draw.rectangle([(cx - 2, cy - 2), (cx + 2, cy + 2)], fill=(0, 255, 200))
    
    def _add_authority_elements(self, draw, member_index, font):
        """Add authority badge elements for realistic conference badge appearance."""
        # Bottom authority strip
        draw.rectangle(
            [(0, self.card_height - 35), (self.card_width, self.card_height)],
            fill=(20, 40, 80, 230),
            outline=(0, 200, 255)
        )
        
        # Authorization text
        auth_text = "✓ TechXelarate 2026 Official"
        bbox_auth = draw.textbbox((0, 0), auth_text, font=font)
        auth_width = bbox_auth[2] - bbox_auth[0]
        x_auth = (self.card_width - auth_width) // 2
        draw.text((x_auth, self.card_height - 28), auth_text, fill=(0, 255, 150), font=font)
    
    def _create_placeholder_image(self, size: int) -> PILImage.Image:
        """Create attractive placeholder image."""
        img = PILImage.new('RGB', (size, size), (50, 60, 100))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient circle
        for r in range(size // 2, 0, -1):
            intensity = int(100 + 155 * (1 - r / (size // 2)))
            color = (intensity, intensity + 20, intensity + 50)
            draw.ellipse([(size//2 - r, size//2 - r), (size//2 + r, size//2 + r)], fill=color)
        
        # Draw user icon
        center = size // 2
        draw.ellipse([(center - 40, center - 60), (center + 40, center - 20)], fill=(200, 200, 220))
        draw.ellipse([(center - 50, center), (center + 50, center + 80)], fill=(200, 200, 220))
        
        return img
    
    def _generate_participant_qr_code(self, team_data: dict, member: dict, member_index: int) -> PILImage.Image:
        """Generate unique QR code for each participant (for attendance check-in)."""
        # Generate unique participant code
        participant_id = member.get('participant_id', f"{team_data.get('team_id', 'TEK')}-{member_index:03d}")
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=15,
            border=2,
        )
        qr.add_data(participant_id)
        qr.make(fit=True)
        
        # Black QR code on white for high contrast scanning
        qr_img = qr.make_image(fill_color="black", back_color="white")
        return qr_img.convert('RGB')
    
    def _create_text_card(self, team_data: dict, member: dict) -> list:
        """Fallback: Create text-based ID card using Platypus with premium styling."""
        elements = []
        styles = getSampleStyleSheet()
        
        # Define custom premium styles
        title_style = ParagraphStyle(
            'CardTitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#00E8FF'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        name_style = ParagraphStyle(
            'ParticipantName',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#FFFFFF'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#D0D0D0'),
            spaceAfter=2,
            alignment=TA_CENTER
        )
        
        # Build card content
        elements.append(Paragraph("🎓 LBRCE - TECHXELARATE 2026", title_style))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph(member.get('name', 'Participant').upper()[:30], name_style))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph(f"Team: {team_data.get('team_name', 'Unknown')}", info_style))
        participant_id = member.get('participant_id', 'GEN-000000')
        elements.append(Paragraph(f"Participant ID: {participant_id}", info_style))
        elements.append(Spacer(1, 0.08*inch))
        
        domain = team_data.get('domain', 'AI')
        year = team_data.get('year', 'I')
        elements.append(Paragraph(f"Domain: {domain} | Year: {year}", info_style))
        elements.append(Spacer(1, 0.1*inch))
        
        quote = get_random_quote()
        quote_text = f'"{quote}"' if len(quote) < 60 else f'"{quote[:60]}..."'
        elements.append(Paragraph(quote_text, info_style))
        
        return elements
    
    def generate_participant_qr_pngs(
        self,
        team_data: dict,
        team_members_list: list
    ) -> dict:
        """
        Generate individual QR code PNG images for each participant.
        These PNGs can be printed/displayed for attendance checking.
        
        Args:
            team_data: Dictionary with team information
            team_members_list: List of team member dictionaries with participant_id
            
        Returns:
            Dictionary with participant_id -> qr_png_path mapping
        """
        try:
            qr_paths = {}
            team_id = team_data.get('team_id')
            
            for idx, member in enumerate(team_members_list):
                participant_id = member.get('participant_id', f"{team_id}-{idx:03d}")
                
                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=20,
                    border=3,
                )
                qr.add_data(participant_id)
                qr.make(fit=True)
                
                # Create PNG image (large enough for printing)
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                # Save as PNG
                qr_filename = f"{team_id}_qr_{participant_id}_Large.png"
                qr_path = os.path.join(self.output_dir, qr_filename)
                qr_img.save(qr_path, 'PNG')
                
                qr_paths[participant_id] = qr_path
                logger.info(f"✓ QR PNG generated for {participant_id}: {qr_path}")
            
            return qr_paths
        
        except Exception as e:
            logger.error(f"Error generating QR PNGs: {str(e)}")
            raise Exception(f"Failed to generate participant QR PNGs: {str(e)}")


