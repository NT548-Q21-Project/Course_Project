import * as pdfjsLib from "pdfjs-dist";

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString();

export async function extractTextFromPDF(url: string) {
  // fetch raw file
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("Cannot fetch PDF");
  }

  // lấy blob
  const blob = await response.blob();

  // ép MIME type nếu cloudinary không trả đúng
  const pdfBlob = new Blob([blob], {
    type: "application/pdf",
  });

  // convert sang array buffer
  const arrayBuffer = await pdfBlob.arrayBuffer();

  // load pdf
  const pdf = await pdfjsLib.getDocument({
    data: arrayBuffer,
  }).promise;

  let fullText = "";

  // đọc từng page
  for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
    const page = await pdf.getPage(pageNum);

    const textContent = await page.getTextContent();

    const pageText = textContent.items
      .map((item: any) => item.str)
      .join(" ");

    fullText += pageText + "\n";
  }

  return fullText;
}