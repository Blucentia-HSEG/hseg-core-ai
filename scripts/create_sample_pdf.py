from fpdf import FPDF

sample_text = (
    "q23: What would you change about your workplace?\n"
    "I feel like my boss is constantly undermining me. He is a bully and I am afraid to speak up. "
    "I have seen him target others as well, especially women. I am scared of retaliation, but someone needs to do something. "
    "This is not a safe environment.\n\n"
    "q24: How does work impact your mental health?\n"
    "The stress is unbearable. I have panic attacks just thinking about coming to work. "
    "I can't sleep and I am constantly anxious. I feel like I am on the verge of a breakdown. "
    "I have told my manager about my workload, but he just tells me to 'suck it up'.\n\n"
    "q25: What is one thing your workplace does well?\n"
    "I guess the pay is okay. But it's not worth the mental toll. I am actively looking for another job. "
    "I used to be optimistic about my future here, but now I just feel dread."
)

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, txt=sample_text)
pdf.output("docs/sample_communication_analysis.pdf")

print("Successfully created docs/sample_communication_analysis.pdf")
