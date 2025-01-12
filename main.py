import pdfExtractor
from googleCalendar import create_schedule_calendar


def main():
    print("Enter the pdf file path: ", end="")
    pdf_path = input()
    try:
        pdfExtractor.extract_schedule(pdf_path)
        create_schedule_calendar()
    except Exception as e:
        print(e)



if __name__ == "__main__":
    main()