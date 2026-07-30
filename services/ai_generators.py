import json
from models.lead import Lead

def get_portfolio_matches(category: str) -> list:
    cat = category.lower() if category else ""
    if "hotel" in cat or "resort" in cat or "tourism" in cat:
        return ["Nilgiris Explorers", "Luxury Retreats Portfolio"]
    elif "flower" in cat or "florist" in cat:
        return ["House Of Petalss"]
    elif "restaurant" in cat or "cafe" in cat or "food" in cat:
        return ["Restaurant Template", "Bistro Demo"]
    elif "dentist" in cat or "hospital" in cat or "clinic" in cat:
        return ["Health & Wellness Template"]
    elif "salon" in cat or "spa" in cat or "beauty" in cat:
        return ["Beauty Studio Portfolio"]
    else:
        return ["Personal Portfolio", "Corporate Business Template"]

class ProposalGenerator:
    def __init__(self):
        self.templates = {
            "default": """
# Website Opportunity Proposal for {business_name}

## Executive Summary
{business_name} has a significant opportunity to capture more customers and increase trust by establishing a professional digital presence. Based on our analysis, your current Website Opportunity Score is **{opportunity_score}/100**, placing you in the **{lead_priority}** category for immediate digital growth.

## Core Issues Identified
{problems}

## Business Impact
Without resolving these issues, {business_name} is likely losing potential customers to competitors with stronger, more accessible digital platforms. Relying solely on third-party platforms or having no web presence reduces trust and limits your direct booking/sales capabilities.

## Recommended Solution
We propose a comprehensive digital foundation including:
{solutions}

## Suggested Portfolio References
We have built successful websites for similar businesses. Check out these examples:
{portfolio}

## Timeline
Estimated project duration: 3-5 weeks.

## Estimated Investment
Based on the required scope and industry standards: **₹{estimated_value:,.2f}**

## Call To Action
Let's schedule a brief 15-minute call to discuss how we can build your digital presence and drive more revenue for {business_name}.
"""
        }

    def generate(self, lead: Lead) -> str:
        problems = []
        solutions = []
        
        if lead.website_type == "None":
            problems.append("- No professional website exists. Relying entirely on offline or third-party discovery.")
            solutions.append("- Build a custom, mobile-responsive professional website.")
        elif lead.website_type in ["Facebook", "Instagram", "WhatsApp"]:
            problems.append(f"- Relying exclusively on {lead.website_type} for web presence limits brand authority and control.")
            solutions.append("- Establish an independent domain and brand-controlled website.")
        else:
            if lead.has_ssl == "No":
                problems.append("- Website lacks SSL encryption (Not Secure).")
                solutions.append("- Implement standard SSL certificate for security and trust.")
            if lead.is_mobile_responsive == "No":
                problems.append("- Website is not mobile responsive, hurting mobile traffic.")
                solutions.append("- Redesign with a mobile-first responsive framework.")
            if lead.has_online_booking == "No":
                problems.append("- Missing online booking/appointment functionality, creating friction for customers.")
                solutions.append("- Integrate an automated online booking system to capture leads 24/7.")
                
        if lead.has_professional_email == "No":
            problems.append("- Using a free email provider (e.g., Gmail/Yahoo) reduces professional credibility.")
            solutions.append("- Set up professional business email accounts (e.g., contact@{domain}).")
            
        if not problems:
            problems.append("- Website exists but can be optimized for higher conversions.")
            solutions.append("- Advanced SEO and conversion rate optimization (CRO).")
            
        portfolio_links = "\n".join([f"- {p}" for p in get_portfolio_matches(lead.category)])
            
        return self.templates["default"].format(
            business_name=lead.business_name,
            opportunity_score=lead.opportunity_score,
            lead_priority=lead.priority,
            problems="\n".join(problems),
            solutions="\n".join(solutions),
            portfolio=portfolio_links,
            estimated_value=lead.estimated_value or 35000.0,
            domain=lead.business_name.lower().replace(" ", "") + ".com"
        )

class EmailGenerator:
    def generate(self, lead: Lead, style: str = "Professional") -> str:
        subject = f"Digital Growth Opportunity for {lead.business_name}"
        
        body = f"Hello,\n\nI specialize in helping businesses like {lead.business_name} establish a strong online presence to drive more revenue.\n\n"
        
        if lead.website_type == "None":
            body += f"I noticed that {lead.business_name} currently doesn't have a professional website. "
        elif lead.website_type in ["Facebook", "Instagram"]:
            body += f"I noticed you are currently relying on {lead.website_type} for your online presence. While great for social engagement, a dedicated website builds significantly more trust. "
        else:
            body += f"I ran an audit on your website and found some technical bottlenecks that might be costing you customers. "
            if lead.has_online_booking == "No":
                body += "For instance, integrating a direct online booking system could immediately increase your conversion rate. "
                
        if lead.has_professional_email == "No":
            body += "Also, upgrading from a free email to a professional domain email will instantly boost your brand's credibility.\n\n"
            
        body += "I have relevant portfolio work in your industry and would love to show you what's possible.\n\n"
        body += "Would you be open to a quick 10-minute chat next week to discuss?\n\nBest regards,"
        
        return f"Subject: {subject}\n\n{body}"

class WhatsAppGenerator:
    def generate(self, lead: Lead, style: str = "Medium Message") -> str:
        msg = f"Hi {lead.business_name} team! 👋 I'm a web developer and noticed a huge opportunity for your business online. "
        
        if lead.website_type == "None":
            msg += "You currently don't have a website, which means you're missing out on Google search traffic. "
        elif lead.website_type in ["Facebook", "Instagram"]:
            msg += f"Relying only on {lead.website_type} is great for social, but a real website builds massive trust. "
        else:
            msg += "Your current website has a few technical issues holding back traffic. "
            
        msg += "I'd love to help you fix this and bring in more customers. Are you available for a quick chat today?"
        return msg

class CallScriptGenerator:
    def generate(self, lead: Lead) -> str:
        script = f"""
[INTRO]
"Hi, is this the owner or manager of {lead.business_name}? 
My name is [Your Name], and I'm a web developer specializing in your industry."

[HOOK]
"""
        if lead.website_type == "None":
            script += f'"I was looking for your services online and noticed you don\'t have a professional website yet. Customers are searching for you on Google, and right now, they can\'t find a dedicated site to build trust with."'
        elif lead.website_type in ["Facebook", "Instagram"]:
            script += f'"I saw your {lead.website_type} page, which looks great, but I noticed you don\'t have an official website. A lot of customers look for a real website before making a purchasing decision."'
        else:
            script += f'"I was reviewing your website and noticed it\'s missing a few key features like online booking and mobile optimization that are causing you to lose customers."'

        script += f"""

[VALUE PROPOSITION]
"I've built websites for similar businesses (like {get_portfolio_matches(lead.category)[0]}) and helped them increase their direct inquiries by over 40%. 
I have a few specific ideas on how we can do the same for {lead.business_name}."

[CALL TO ACTION]
"I know you're busy running the business. Can we schedule a quick 10-minute Zoom call on Tuesday where I can show you exactly what I mean? No pressure at all."
"""
        return script.strip()

class MeetingPointsGenerator:
    def generate(self, lead: Lead) -> str:
        points = f"""
# Discovery Meeting Talking Points for {lead.business_name}

1. **Current Situation & Pain Points**
   - Goal: Understand how they currently get customers.
   - Question: "How much of your business currently comes from online searches vs word-of-mouth?"

2. **The Website Opportunity (Score: {lead.opportunity_score}/100)**
"""
        if lead.website_type in ["None", "Facebook", "Instagram", "WhatsApp"]:
            points += f"   - Highlight the massive gap: Relying on offline/social media limits scalability and trust.\n"
        else:
            points += f"   - Highlight the technical gaps (e.g. no booking, slow speeds, poor SEO).\n"
            
        points += f"""
3. **Credibility & Trust**
"""
        if lead.has_professional_email == "No":
            points += f"   - Mention how moving to a professional email (e.g., info@domain.com) increases trust instantly.\n"

        points += f"""
4. **Showcase Portfolio**
   - Present: {", ".join(get_portfolio_matches(lead.category))}
   - Explain how these businesses benefited from a custom website.

5. **Financial ROI (Estimated Project Value: ₹{lead.estimated_value:,.2f})**
   - Explain that a website is an investment, not an expense. Calculate how many new customers they need to break even.
   - Discuss Timeline (3-5 weeks).

6. **Next Steps**
   - Agree on the scope and send the customized proposal.
"""
        return points.strip()

proposal_gen = ProposalGenerator()
email_gen = EmailGenerator()
whatsapp_gen = WhatsAppGenerator()
call_script_gen = CallScriptGenerator()
meeting_points_gen = MeetingPointsGenerator()
