import { Routes } from '@angular/router';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { ProjectsComponent } from './pages/projects/projects.component';
import { PipelinesComponent } from './pages/pipelines/pipelines.component';
import { ProjectDetailsComponent } from './pages/project-details/project-details.component';


export const routes: Routes = [
    { path: '', component: DashboardComponent },
    { path: 'projects', component: ProjectsComponent },
    { path: 'projects/:id', component: ProjectDetailsComponent },
    { path: 'pipelines', component: PipelinesComponent },
  ];