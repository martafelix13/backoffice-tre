import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class TaskService {

  backendUrl = 'http://localhost:8081/api';

  constructor(private http: HttpClient) { }

  getTasks() {
    return this.http.get(`${this.backendUrl}/tasks`);
  }
}
