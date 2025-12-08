export async function uploadPdf(file: File, apiUrl: string): Promise<any> {
  if (!(file instanceof File)) {
    throw new Error('Invalid file provided. Expected a File object.');
  }

  const formData = new FormData();
  formData.append('pdfFile', file); // 'pdfFile' is the field name your backend expects

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      body: formData,
      // When sending FormData, the 'Content-Type' header is automatically set
      // to 'multipart/form-data' by the browser, including the boundary.
      // Do NOT set it manually here.
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(`PDF upload failed: ${response.status} ${response.statusText} - ${errorData.message || ''}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading PDF:', error);
    throw error;
  }
}
