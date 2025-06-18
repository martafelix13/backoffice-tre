import { Component } from '@angular/core';
import { TaskService } from '../../services/task.service';

@Component({
  selector: 'app-tasks-validation',
  imports: [],
  templateUrl: './tasks-validation.component.html',
  styleUrl: './tasks-validation.component.scss'
})
export class TasksValidationComponent {

  constructor(private taskService: TaskService) { }

  ngOnInit(): void {
    window.location.href = 'http://localhost:10001/browser/tes';
  }
}
