import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface LegalDocumentTemplate {
  selected: boolean;
  filename: string;
}

export interface SignedFile {
  filename: string;
  path: string;
  verified: boolean;
  feedback: string | null;
}

@Injectable({
  providedIn: 'root'
})

export class DocumentWorkflowService {
  private apiUrl = 'http://localhost:8081/files'; // Adjust this base URL as needed

  constructor(private http: HttpClient) {}

  getTemplates(): Observable<LegalDocumentTemplate[]> {
    return this.http.get<LegalDocumentTemplate[]>(`${this.apiUrl}/templates`);
  }

  downloadTemplate(filename: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/templates/${filename}`, {
      responseType: 'blob'
    });
  }

  downloadSignedDocument(projectId: string, filename: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/signed/${projectId}/${filename}`, {
      responseType: 'blob'
    });
  }

  getSignedFileDownloadUrl(projectId: string, filename: string): string {
    return `${this.apiUrl}/signed/${projectId}/${filename}`;
  }

  getTemplateDownloadUrl(filename: string): string {
    return `${this.apiUrl}/templates/${filename}`;
  }

  deleteTemplate(filename: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/templates/${filename}`);
  }

  uploadTemplate(file: File): Observable<any>  {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/upload-template`, formData);
  }

  assignTemplates(projectId: string, templates: string[]): Observable<any> {
    return this.http.post(`${this.apiUrl}/assign-templates/${projectId}`, templates);
  }

  validateFile(projectId: string, filename: string, approved: boolean, feedback?: string): Observable<any> {
    const data = {
      filename: filename,
      approved: approved,
      feedback: feedback || ''
    }
    console.log(`Validating file: ${filename}, Approved: ${approved}, Feedback: ${feedback}`);
    return this.http.post(`${this.apiUrl}/validate-file/${projectId}`, data);
  }
}
