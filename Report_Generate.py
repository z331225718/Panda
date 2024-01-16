from win32com import client
from re import match
import os

class ReportGenerator:
    def __init__(self,file):
        self.word = client.DispatchEx("Word.Application")
        self.word.Visible = 0
        self.doc = self.word.Documents.Add()
        self.path,self.filename = os.path.split(file)

    def Set_title_to_word(self):
        Heading1 = self.doc.Styles(-2)
        Heading2 = self.doc.Styles(-4)
        Heading3 = self.doc.Styles(-5)
        FirstTitle = r'^\d\.[^\d].+\r$'
        ScondTitle = r'^\d\.\d[^\..]+\r$'
        ThirdTitle = r'^\d\.\d\.\d[^\..]+\r$'

        for para in self.doc.Paragraphs:
            if match(FirstTitle, para.Range.Text) != None:
                para.Style = Heading1
            elif match(ScondTitle, para.Range.Text) != None:
                para.Style = Heading2
            elif match(ThirdTitle, para.Range.Text) != None:
                para.Style = Heading3

        self.doc.Range(Start=0, End=0).InsertBreak()
        self.doc.Range(Start=0, End=0).InsertParagraphBefore()
        FirstLineRange = self.doc.Paragraphs(1).Range
        FirstLineRange.Text = 'xxx SIPI Report'
        FirstLineRange.Font.Bold = True
        FirstLineRange.Font.Size = 24
        FirstLineRange.ParagraphFormat.Alignment = 1

        FirstLineRange.InsertParagraphAfter()

        ContentsLineRange = self.doc.Paragraphs(2).Range
        ContentsLineRange.Text = 'Contents'
        ContentsLineRange.Font.Bold = True
        ContentsLineRange.Font.Size = 20
        ContentsLineRange.ParagraphFormat.Alignment = 0
        ContentsLineRange.InsertParagraphAfter()
        ContentsLineRange.InsertParagraphAfter()

        SecondLineRange = self.doc.Paragraphs(3).Range

        self.doc.TablesOfContents.Add(Range=SecondLineRange,
                             UseHeadingStyles=False, LowerHeadingLevel=4)


    def Create_word(self):

        content = [
        "1. Setup",
        "1.1 Spec",
        "1.2 Sim Setting",
        "2. SI Result",
        "2.1 Host Side",
        "2.1.1 HTX Diff RL",
        "2.1.2 HTX Diff IL",
        "2.1.3 HTX FEXT",
        "2.1.4 HTX Comm RL",
        "2.1.5 HTX SDC RL",
        "2.1.6 HRX Diff RL",
        "2.1.7 HRX Diff IL",
        "2.1.8 HRX FEXT",
        "2.1.9 HRX Comm RL",
        "2.1.10 HRX SDC RL",
        "2.1.11 Host NEXT",
        "2.2 Line Side",
        "2.2.1 LTX Diff RL",
        "2.2.2 LTX Diff IL",
        "2.2.3 LTX Single-ended RL",
        "2.2.4 LTX FEXT",
        "2.2.5 LTX Comm RL",
        "2.2.6 LTX SDC RL",
        "2.2.7 LRX Diff RL",
        "2.2.8 LRX Diff IL",
        "2.2.9 LRX FEXT",
        "2.2.10 LRX Comm RL",
        "2.2.11 LRX SDC RL",
        "2.2.12 Line NEXT",
        "3. PI Result",
        "3.1 DC IR Drop",
        "3.2 Mission Mode Ripple",
        "4. Conclusion"
        ]
        for line in content:
        # 向文档中添加一个新的段落
            para = self.doc.Content.Paragraphs.Add()
        # 将内容添加到段落中
            para.Range.Text = line
        # 添加一个回车符，结束段落
            para.Range.InsertParagraphAfter()



    def find_png_files(self):
        """查找路径下所有.png文件并把文件名记录到list中"""
        png_paths = []
        for root, dir, files in os.walk(self.path):
            for file in files:
                if file.endswith(".png"):
                    png_paths.append(os.path.join(root, file))
        return png_paths


    def Contains_all_strings(self,target_str, string_set):
        for s in string_set:
            if target_str.find(s) == -1:
                return False
        return True


    def Add_result_to_word(self):
        paragraphs = self.doc.Paragraphs
        result_path = self.find_png_files()
        for i in range(len(result_path)):
            for j, para in enumerate(paragraphs):
                if self.Contains_all_strings(para.Range.Text, result_path[i].split("\\")[-1].split('.')[0].split('_')):
                    NextPara = para.Range.Paragraphs.Add()
                    NextPara.Range.InsertParagraphBefore()
                    pic = NextPara.Range.InlineShapes.AddPicture(
                        result_path[i], False, True)
                    pic.Width = 15*28
                    pic.Height = 8*28
                    NextPara.Range.ParagraphFormat.Alignment = 1
                    break
    
    def Save_and_exit(self):
        self.doc.save()
        self.word.Quit()


if __name__ == '__main__':
    file = r'./temp.docx'
    png_path = r'./'
    report_generator = ReportGenerator(file)
    report_generator.Create_word()
    report_generator.Add_result_to_word()
    report_generator.Set_title_to_word()
