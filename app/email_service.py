"""
Professional email service for hackathon registration and ID card delivery.
Handles OTP emails, registration confirmation, and ID card distribution with attachments.
"""
import resend
import smtplib
import os
import logging
from email.message import EmailMessage
from .config import settings
from .quotes import get_random_quote
resend.api_key = "re_NfLHXoiF_NmdR1X7vJKwdz62kWBec3G33"

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails."""
    
    
    @staticmethod
    def send_registration_confirmation(
        to_email: str,
        leader_name: str,
        team_name: str,
        team_id: str,
        college_name: str,
        domain: str,
        year: str,
        team_members: list[dict]
    ) -> bool:
        """
        Send registration confirmation email including full team details.
        Attachments are disabled; only text/HTML content is sent.
        
        Args:
            to_email: Recipient email address
            leader_name: Team leader name
            team_name: Team name
            team_id: Team unique identifier
            college_name: Name of the institution
            domain: Selected hackathon domain/track
            team_members: List of dictionaries with member info (name, email, phone, etc.)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            logger.info(f"📧 Preparing registration confirmation email for {to_email}")
            message = EmailMessage()
            message["From"] = settings.SMTP_USER
            message["To"] = to_email
            message["Subject"] = "✅ TechXelarate - Registration Confirmed!"
            
            # construct plain text listing of members
            member_lines = []
            for idx, m in enumerate(team_members, start=1):
                name = m.get("name") or "(unknown)"
                email = m.get("email") or ""
                phone = m.get("phone") or ""
                leader_marker = " (Leader)" if m.get("is_team_leader") else ""
                member_lines.append(f"{idx}. {name}{leader_marker} - {email} {phone}")

            member_section = "\n".join(member_lines)

            plain_body = f"""
TechXelarate 2026 - Registration Confirmed!

Hello {leader_name},

Congratulations! Your team '{team_name}' has been successfully registered for TechXelarate 2026.

Team ID: {team_id}
College/Institution: {college_name}
Academic Year: {year}
Domain/Track: {domain}

Team Members:
{member_section}

✅ What's Next:
1. Save this Team ID for event check-in
2. Share it with your team members

💳 Please complete your registration payment by visiting:
https://forms.gle/JTEqHwzVtraKxW9s5


🎉 We're excited to see your innovative ideas come to life!

Event Details:
- 6-Hour Hackathon
- Laki Reddy Bali Reddy College of Engineering
- CSE (AI & ML) Department

Questions? Reply to this email or contact us.

Best Regards,
TechXelarate Team
"""
            
            # build HTML rows for team members
            member_rows = []
            for m in team_members:
                name = m.get("name", "")
                email = m.get("email", "")
                phone = m.get("phone", "")
                leader_label = "<strong>(Leader)</strong>" if m.get("is_team_leader") else ""
                member_rows.append(
                    f"<tr><td style='padding:5px 10px;'>{name} {leader_label}</td>"
                    f"<td style='padding:5px 10px;'>{email}</td>"
                    f"<td style='padding:5px 10px;'>{phone}</td></tr>"
                )
            member_table = "".join(member_rows)

            html_body = f"""
<html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; background-color: #0a0e27;">
        <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                    padding: 40px; border-radius: 12px; border: 2px solid #00ff88; color: #fff;">
            
            <h1 style="text-align: center; color: #00ff88; margin: 0 0 10px 0; font-size: 28px;">✅ Registration Confirmed!</h1>
            <h2 style="text-align: center; color: #00e8ff; margin: 0 0 30px 0; font-size: 18px;">🎉 TechXelarate 2026</h2>

            <!-- payment button section -->
            <div style="text-align: center; margin-top: 20px;">
              <a href="https://forms.gle/JTEqHwzVtraKxW9s5" target="_blank" 
                 style="
                    display: inline-block;
                    padding: 12px 25px;
                    background: linear-gradient(90deg, #00e8ff, #0077ff);
                    color: #ffffff;
                    text-decoration: none;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    box-shadow: 0 4px 15px rgba(0, 232, 255, 0.4);
                    transition: all 0.3s ease;
                 "
                 onmouseover="this.style.transform='scale(1.05)'"
                 onmouseout="this.style.transform='scale(1)';">
                 💳 Click Here to Make Payment
              </a>
            </div>
            <!-- end payment section -->
            
            <p style="color: #d0d0d0; font-size: 16px; margin: 0 0 20px 0;">
                Hello <strong>{leader_name}</strong>,
            </p>
            
            <p style="color: #c0c0c0; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0;">
                Congratulations! Your team <strong style="color: #00ff88;">'{team_name}'</strong> has been successfully registered for 
                <strong style="color: #00e8ff;">TechXelarate 2026</strong>.
            </p>
            
            <!-- Team Info -->
            <p style="color: #d0d0d0; font-size: 14px; margin: 10px 0;">
                <strong>College:</strong> {college_name}<br>
                <strong>Academic Year:</strong> {year}<br>
                <strong>Domain/Track:</strong> {domain}
            </p>

            <!-- Team ID Block -->
            <div style="background: linear-gradient(90deg, rgba(0,255,136,0.2) 0%, rgba(0,232,255,0.1) 100%); 
                        border: 3px solid #00ff88; padding: 20px; border-radius: 10px; 
                        margin: 25px 0; text-align: center;">
                <div style="font-size: 32px; font-weight: bold; color: #00ff88; font-family: 'Courier New', monospace; 
                            background: rgba(0,255,136,0.1); padding: 15px; border-radius: 8px; margin: 10px 0;">
                    {team_id}
                </div>
                <p style="color: #ffaa00; margin: 8px 0 0 0; font-size: 12px; font-weight: bold;">
                    💾 Save this Team ID - you'll need it for event check-in!
                </p>
            </div>

            <!-- Members Table -->
            <table style="width:100%; border-collapse: collapse; color: #d0d0d0;">
                <thead>
                    <tr>
                        <th style="text-align:left; padding:5px;">Name</th>
                        <th style="text-align:left; padding:5px;">Email</th>
                        <th style="text-align:left; padding:5px;">Phone</th>
                    </tr>
                </thead>
                <tbody>
                    {member_table}
                </tbody>
            </table>
            
            <!-- Footer -->
            <div style="border-top: 1px solid #00e8ff; margin-top: 30px; padding-top: 20px; 
                        text-align: center; color: #808080; font-size: 12px;">
                <p style="margin: 8px 0; color: #d0d0d0;">
                    🚀 We're excited to see your innovative ideas come to life!
                </p>
                <p style="margin: 8px 0;">© 2026 TechXelarate | CSE (AI & ML) - LBRCE</p>
                <p style="margin: 5px 0; color: #606060; font-size: 11px;">
                    Questions? Reply to this email or contact us at lbrcehackcsm@gmail.com
                </p>
            </div>
        </div>
    </body>
</html>
"""
            
            message.set_content(plain_body)
            message.add_alternative(html_body, subtype="html")
            
            # no attachments
            
            # Send email
            
            resend.Emails.send({
    "from": "TechXelarate <team@techxelerate.co.in>",
    "to": [to_email],
    "subject": message["Subject"],
    "html": html_body
})
            logger.info(f"✅ Registration confirmation sent to {to_email}")
            print(f"✅ Confirmation Email Sent: {to_email}")
            return True
        
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error while sending confirmation to {to_email}: {e}")
            return False
        except Exception as e:
            logger.exception(f"❌ Exception sending confirmation email: {e}")
            return False
    
    
    @staticmethod
    def send_otp_email(to_email: str, otp: str) -> bool:
        """
        Send OTP verification email.
        
        Args:
            to_email: Recipient email address
            otp: One-time password (6 digits)
            
        Returns:
            True if email sent successfully, False otherwise
        """     
        try:
            logger.info(f"📧 Preparing OTP email for {to_email}")
            message = EmailMessage()
            message["From"] = settings.SMTP_USER
            message["To"] = to_email
            message["Subject"] = "🔐 TechXelarate Hackathon - Your OTP Verification Code"
            
            plain_body = f"""
TechXelarate 2026 - Hackathon Registration

Your One-Time Password (OTP) for registration verification:

{otp}

⏱️ Important: This OTP expires in 5 minutes.
🔒 Never share this code with anyone.

If you didn't request this OTP, please ignore this email.

Event: TechXelarate 2026 - 6-Hour Hackathon
College: Laki Reddy Bali Reddy College of Engineering
Department: CSE (AI & ML)

---
TechXelarate Team
"""
            
            html_body = f"""
<html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; background-color: #0a0e27;">
        <div style="max-width: 500px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                    padding: 30px; border-radius: 10px; border: 2px solid #00e8ff; color: #fff;">
            
            <h2 style="text-align: center; color: #00e8ff; margin: 0 0 10px 0;">🎉 TechXelarate 2026</h2>
            <h3 style="text-align: center; color: #c800ff; margin: 0 0 25px 0;">Hackathon Registration</h3>
            
            <p style="color: #e0e0e0; font-size: 16px; margin: 15px 0;">
                Your One-Time Password (OTP) for registration verification:
            </p>
            
            <div style="background-color: rgba(0, 232, 255, 0.1); border: 2px solid #00e8ff; padding: 20px; 
                        border-radius: 8px; text-align: center; margin: 25px 0; border-left: 5px solid #c800ff;">
                <div style="font-size: 36px; font-weight: bold; color: #00ff88; letter-spacing: 5px; font-family: 'Courier New', monospace;">
                    {otp}
                </div>
            </div>
            
            <div style="background-color: rgba(200, 0, 255, 0.1); border-left: 4px solid #c800ff; padding: 12px; 
                        border-radius: 4px; margin: 20px 0; color: #ffaaff;">
                <strong>⏱️ Important:</strong> This code expires in <strong>5 minutes</strong>.
            </div>
            
            <p style="color: #a0a0a0; font-size: 14px; margin: 15px 0;">
                🔒 For your security, never share this code with anyone, not even event organizers.
            </p>
            
            <div style="border-top: 1px solid #00e8ff; margin-top: 25px; padding-top: 20px; color: #a0a0a0; font-size: 12px;">
                <p style="margin: 5px 0;"><strong style="color: #00e8ff;">Event:</strong> TechXelarate 2026 - 6-Hour Hackathon</p>
                <p style="margin: 5px 0;"><strong style="color: #00e8ff;">College:</strong> Laki Reddy Bali Reddy College of Engineering</p>
                <p style="margin: 5px 0;"><strong style="color: #00e8ff;">Department:</strong> CSE (AI & ML)</p>
            </div>
            
            <div style="text-align: center; margin-top: 25px; color: #707070; font-size: 11px;">
                <p>© 2026 TechXelarate. All rights reserved.</p>
            </div>
        </div>
    </body>
</html>
"""
            
            message.set_content(plain_body)
            message.add_alternative(html_body, subtype="html")
            
            # Send email
            
            resend.Emails.send({
    "from": "TechXelarate <team@techxelerate.co.in>",
    "to": [to_email],
    "subject": message["Subject"],
    "html": html_body
})
            logger.info(f"✅ OTP email delivered successfully to {to_email} | Code: {otp}")
            print(f"✅ OTP Sent: {to_email}")  # Also print to console
            return True
        
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP authentication failed: {e}. Check email credentials in .env")
            print(f"❌ AUTH ERROR: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error while sending OTP to {to_email}: {e}")
            print(f"❌ SMTP ERROR: {e}")
            return False
        except Exception as e:
            logger.exception(f"❌ Exception sending OTP email to {to_email}: {e}")
            return False
    
    @staticmethod
    def send_id_cards_email(
        to_email: str,
        team_id: str,
        team_name: str,
        leader_name: str,
        id_cards_pdf_path: str,
        domain: str = "General"
    ) -> bool:
        """
        Send professional ID cards PDF via email after registration.
        Includes unique QR codes for each participant (embedded in cards for scanning).
        Includes unique team code for attendance verification.
        Includes random motivational quote and professional formatting.
        
        Args:
            to_email: Recipient email address
            team_id: Team identifier
            team_name: Team name
            leader_name: Team leader name
            id_cards_pdf_path: Path to the generated ID cards PDF file
            domain: Selected hackathon domain/track
            Note: QR now contains `team_id` and `access_key` only
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Check PDF exists before creating message
            if not id_cards_pdf_path or not os.path.exists(id_cards_pdf_path):
                logger.error(f"❌ ID cards PDF not found: {id_cards_pdf_path}")
                return False
            
            # Get random motivational quote
            quote = get_random_quote()
            
            message = EmailMessage()
            message["From"] = settings.SMTP_USER
            message["To"] = to_email
            message["Subject"] = "🏆 TechXelarate - Your Official Hackathon ID Cards"
            
            plain_body = f"""

Hello {leader_name},

Congratulations! Your team '{team_name}' has been successfully registered for TechXelarate 2026.


TEAM DETAILS:
─────────────────────────────────────
Team ID:        {team_id}
Team ID:        {team_id}
Team Name:      {team_name}
Domain/Track:   {domain}
Event:          TechXelarate 2026 - 6-Hour Hackathon
Institution:    Laki Reddy Bali Reddy College of Engineering
Department:     CSE (AI & ML)

YOUR ID CARDS:
─────────────────────────────────────
✓ One professional badge per team member
✓ Unique participant code on each card  
✓ QR code for instant check-in scanning at the event
✓ Premium photo-badge design with college branding

HOW ATTENDANCE WORKS:
─────────────────────────────────────
1. Each card has a unique QR code
2. Scan the QR code at event check-in
3. Your attendance will be instantly recorded in our system
4. All team members must check-in separately

MOTIVATION:
💡 "{quote}"

Need Help?
If you have any questions or concerns, please reply to this email
or contact the organizers at lbrcehackcsm@gmail.com

We're excited to see your innovative ideas come to life!

Best Regards,
TechXelarate Team
CSE (AI & ML) - LBRCE
"""
            
            html_body = f"""
<html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; background-color: #0a0e27;">
        <div style="max-width: 700px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                    padding: 40px; border-radius: 12px; border: 2px solid #00e8ff; color: #fff; box-shadow: 0 10px 40px rgba(0,232,255,0.2);">
            
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #c800ff; padding-bottom: 20px;">
                <h1 style="color: #00e8ff; margin: 0; font-size: 28px;">🎉 TechXelarate 2026</h1>
            </div>
            
            <!-- Greeting -->
            <p style="color: #e0e0e0; font-size: 16px; margin: 0 0 15px 0;">
                Hello <strong>{leader_name}</strong>,
            </p>
            
            <p style="color: #d0d0d0; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0;">
                Congratulations! Your team <strong style="color: #00ff88;">'{team_name}'</strong> has been successfully registered for 
                <strong style="color: #00e8ff;">TechXelarate 2026</strong>, the premier 6-hour hackathon event at LBRCE.
            </p>
            
            <!-- Team Details Card -->
            <div style="background: linear-gradient(90deg, rgba(0,232,255,0.2) 0%, rgba(200,0,255,0.2) 100%); 
                        border: 2px solid #00e8ff; border-left: 5px solid #c800ff; padding: 20px; border-radius: 8px; 
                        margin: 25px 0; color: #fff;">
                <h3 style="color: #00e8ff; margin: 0 0 12px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
                    📋 Team Details
                </h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #00e8ff; opacity: 0.5;">
                        <td style="padding: 8px 0; color: #a0a0f0;"><strong>Team ID:</strong></td>
                        <td style="padding: 8px 0; color: #00ff88; font-family: 'Courier New', monospace; text-align: right;">{team_id}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #00e8ff; opacity: 0.5;">
                        <td style="padding: 8px 0; color: #a0a0f0;"><strong>Team ID:</strong></td>
                        <td style="padding: 8px 0; color: #00ff88; font-family: 'Courier New', monospace; text-align: right;">{team_id}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #00e8ff; opacity: 0.5;">
                        <td style="padding: 8px 0; color: #a0a0f0;"><strong>Team Name:</strong></td>
                        <td style="padding: 8px 0; color: #ffaa00; text-align: right;">{team_name}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #00e8ff; opacity: 0.5;">
                        <td style="padding: 8px 0; color: #a0a0f0;"><strong>Domain/Track:</strong></td>
                        <td style="padding: 8px 0; color: #ff00ff; text-align: right;">{domain}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #c800ff; opacity: 0.5;">
                        <td style="padding: 8px 0; color: #a0a0f0;"><strong>Event:</strong></td>
                        <td style="padding: 8px 0; color: #88ff00; text-align: right;">6-Hour Hackathon</td>
                    </tr>
                </table>
            </div>
            
            
            <!-- Motivation Quote -->
            <div style="background: linear-gradient(135deg, rgba(200,0,255,0.2) 0%, rgba(0,232,255,0.1) 100%); 
                        border: 2px solid #c800ff; border-radius: 8px; padding: 20px; margin: 25px 0; text-align: center;">
                <p style="color: #ffaaff; font-size: 15px; margin: 0; font-style: italic; line-height: 1.6;">
                    💡 <strong>"{quote}"</strong>
                </p>
            </div>
            
            <!-- Event Info -->
            <div style="background: rgba(0,232,255,0.1); border: 1px solid #00e8ff; border-radius: 6px; 
                        padding: 15px; margin: 25px 0; font-size: 13px; color: #b0b0b0;">
                <h3 style="color: #00e8ff; margin: 0 0 10px 0; font-size: 13px; text-transform: uppercase;">📍 Event Details</h3>
                <p style="margin: 5px 0;"><strong style="color: #00e8ff;">Institution:</strong> Laki Reddy Bali Reddy College of Engineering</p>
                <p style="margin: 5px 0;"><strong style="color: #00e8ff;">Department:</strong> CSE (AI & ML)</p>
                <p style="margin: 5px 0;"><strong style="color: #00e8ff;">Duration:</strong> 6 Hours</p>
                <p style="margin: 5px 0;"><strong style="color: #00e8ff;">Tracks:</strong> Explainable AI | Cybersecurity | Sustainability | Data Intelligence</p>
            </div>
            
            <!-- Support -->
            <div style="background: rgba(255,170,0,0.1); border-left: 4px solid #ffaa00; padding: 15px; 
                        border-radius: 6px; margin: 25px 0;">
                <p style="color: #d0d0d0; margin: 0; font-size: 14px;">
                    <strong>❓ Questions?</strong> Reply to this email or contact us at 
                    <span style="color: #ffaa00; font-family: 'Courier New', monospace;">hackathon@cse.lbrce.edu</span>
                </p>
            </div>
            
            <!-- Footer -->
            <div style="border-top: 1px solid #00e8ff; margin-top: 30px; padding-top: 20px; 
                        text-align: center; color: #808080; font-size: 12px;">
                <p style="margin: 8px 0;">We're excited to see your innovative ideas come to life! 🚀</p>
                <p style="margin: 8px 0; color: #606060;">
                    © 2026 TechXelarate | CSE (AI & ML) - Laki Reddy Bali Reddy College of Engineering
                </p>
                <p style="margin: 5px 0; color: #505050; font-size: 11px;">
                    This is an automated email. Please do not reply with sensitive information.
                </p>
            </div>
        </div>
    </body>
</html>
"""
            
            message.set_content(plain_body)
            message.add_alternative(html_body, subtype="html")
            
            # Attach ID Cards PDF
            try:
                with open(id_cards_pdf_path, 'rb') as f:
                    pdf_data = f.read()
                    message.add_attachment(
                        pdf_data,
                        maintype='application',
                        subtype='pdf',
                        filename=f'{team_id}_id_cards.pdf'
                    )
                logger.info(f"✓ Attached ID cards PDF: {id_cards_pdf_path}")
            except Exception as e:
                logger.error(f"❌ Failed to attach PDF {id_cards_pdf_path}: {e}")
                return False
            
            # Send email
            resend.Emails.send({
    "from": "TechXelarate <team@techxelerate.co.in>",
    "to": [to_email],
    "subject": message["Subject"],
    "html": html_body
})
            
            logger.info(f"✓ ID cards email sent successfully to {to_email}")
            return True
        
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ SMTP authentication failed. Check credentials in .env")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error while sending ID cards to {to_email}: {e}")
            return False
        except Exception as e:
            logger.exception(f"❌ Failed to send ID cards email to {to_email}: {e}")
            return False
