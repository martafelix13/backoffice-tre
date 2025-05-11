import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface Project {
  id: number;
  title: string;
  description: 'Pending' | 'Approved' | 'Rejected';
  deadline: Date;
  status: string;
  organization: string;
  internal_storage: boolean;
  last_update: Date;
  owner: string; 
  legal_documents?: any; // Changed type from [] to any[]
}

@Injectable({
  providedIn: 'root'
})
export class ProjectService {

  constructor(private http: HttpClient) { }

  backendUrl = 'http://localhost:5000/api'

  getProjects(){
    return this.http.get(this.backendUrl + '/projects')
  }
  
  getProject(id: string){
    return this.http.get<Project>(`${this.backendUrl}/projects/${id}`)
  }
    
  createProject(project: Project){
    return this.http.post<Project>(`${this.backendUrl}/projects`, project)
  }

  updateProjectStatus(id: string, newStatus: string){
    return this.http.patch<Project>(`${this.backendUrl}/projects/${id}`, { status: newStatus })
  }

  getProjectFiles(id: string){
    return this.http.get(`${this.backendUrl}/projects/${id}/files`)
  }

  downloadFile(fileid: string){
    return this.http.get(`${this.backendUrl}/files/${fileid}`)
  }
}
