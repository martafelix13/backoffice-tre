import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class PipelineService {

  constructor( private http: HttpClient ) {}

   backendUrl = 'http://localhost:8081/api';

  getPipelines() {
    return this.http.get(`${this.backendUrl}/pipelines`);
  }

  updatePipeline(id: number, data: any) {
    return this.http.put(`${this.backendUrl}/pipelines/${id}`, data);
  }

  createPipeline(data: any) {
    return this.http.post(`${this.backendUrl}/pipelines`, data);
  }

  deletePipeline(id: number) {
    return this.http.delete(`${this.backendUrl}/pipelines/${id}`);
  }
}
