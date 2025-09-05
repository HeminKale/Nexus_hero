import { NextRequest, NextResponse } from "next/server";
import * as XLSX from 'xlsx';

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Helper function to format Excel values properly
function formatExcelValue(value: any): string {
  if (value instanceof Date) {
    // Format date as DD/MM/YYYY to preserve original format and avoid timezone issues
    const day = String(value.getDate()).padStart(2, '0');
    const month = String(value.getMonth() + 1).padStart(2, '0');
    const year = value.getFullYear();
    const formattedDate = `${day}/${month}/${year}`;
    console.log(`🔍 [EXCEL] Date conversion: ${value.toISOString()} → ${formattedDate}`);
    return formattedDate;
  }
  return String(value).trim();
}



export async function POST(req: NextRequest) {
  try {
    console.log('🔍 [EXCEL] Excel parse API called');
    
    const formData = await req.formData();
    console.log('🔍 [EXCEL] FormData received, keys:', Array.from(formData.keys()));
    
    const excelFile = formData.get("excel") as File | null;
    console.log('🔍 [EXCEL] Excel file received:', excelFile ? `${excelFile.name} (${excelFile.size} bytes)` : 'No file');

    if (!excelFile) {
      return NextResponse.json(
        { error: "No Excel file uploaded" },
        { status: 400 }
      );
    }

    // Check file type
    const fileName = excelFile.name.toLowerCase();
    console.log('File validation:', { fileName, type: excelFile.type, size: excelFile.size });
    
    if (!fileName.endsWith('.xlsx') && !fileName.endsWith('.xls')) {
      return NextResponse.json(
        { error: "File must be .xlsx or .xls format" },
        { status: 400 }
      );
    }

    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024;
    if (excelFile.size > maxSize) {
      return NextResponse.json(
        { error: `File size too large. Maximum allowed: 10MB, received: ${(excelFile.size / 1024 / 1024).toFixed(2)}MB` },
        { status: 400 }
      );
    }

    // Convert file to buffer
    const arrayBuffer = await excelFile.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    console.log('Buffer conversion:', { arrayBufferSize: arrayBuffer.byteLength, bufferSize: buffer.length });

    // Parse Excel file
    console.log('Parsing Excel file with buffer size:', buffer.length);
    
    let workbook;
    try {
      workbook = XLSX.read(buffer, { type: 'buffer' });
      console.log('Workbook sheets:', workbook.SheetNames);
    } catch (parseError) {
      console.error('Failed to parse Excel file:', parseError);
      return NextResponse.json(
        { error: `Failed to parse Excel file: ${parseError instanceof Error ? parseError.message : 'Unknown parsing error'}` },
        { status: 400 }
      );
    }
    
    if (!workbook.SheetNames || workbook.SheetNames.length === 0) {
      return NextResponse.json(
        { error: "Excel file contains no sheets" },
        { status: 400 }
      );
    }
    
    const sheetName = workbook.SheetNames[0]; // Get first sheet
    const worksheet = workbook.Sheets[sheetName];
    console.log('Worksheet loaded:', sheetName);

    // Convert to JSON
    let jsonData;
    try {
      jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
      console.log('JSON data extracted, rows:', jsonData.length);
    } catch (jsonError) {
      console.error('Failed to convert worksheet to JSON:', jsonError);
      return NextResponse.json(
        { error: `Failed to convert Excel data: ${jsonError instanceof Error ? jsonError.message : 'Unknown conversion error'}` },
        { status: 400 }
      );
    }

    if (!jsonData || jsonData.length === 0) {
      return NextResponse.json(
        { error: "Excel file is empty or contains no data" },
        { status: 400 }
      );
    }

    // Extract headers (first row)
    const headers = jsonData[0] as string[];
    
    if (!headers || !Array.isArray(headers) || headers.length === 0) {
      return NextResponse.json(
        { error: "Excel file has no valid headers" },
        { status: 400 }
      );
    }
    
    console.log('Headers extracted:', headers);
    
    // Extract data rows (skip header row)
    const rows = jsonData.slice(1).map((row: any) => {
      const rowData: { [key: string]: string } = {};
      headers.forEach((header, index) => {
        rowData[header] = row[index] ? formatExcelValue(row[index]) : '';
      });
      return rowData;
    });

    // Filter out completely empty rows
    const filteredRows = rows.filter(row => 
      Object.values(row).some(value => value !== '')
    );

    console.log('Returning parsed data:', { headers: headers.length, rows: filteredRows.length });
    return NextResponse.json({
      success: true,
      headers: headers,
      rows: filteredRows,
      totalRows: filteredRows.length
    });

  } catch (error) {
    console.error("🔍 [EXCEL] Excel parsing error:", error);
    
    // Enhanced error logging
    if (error instanceof Error) {
      console.error("🔍 [EXCEL] Error message:", error.message);
      console.error("🔍 [EXCEL] Error stack:", error.stack);
    }
    
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    return NextResponse.json(
      { error: `Failed to parse Excel file: ${errorMessage}` },
      { status: 500 }
    );
  }
}
