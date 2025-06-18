import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ProjectService } from '../../services/project.service';
import { convertStatus } from '../../shared/utils/status-converter';
import { MatIconModule } from '@angular/material/icon';
import { AgreementsFragmentComponent } from '../projects/agreements-fragment/agreements-fragment.component';
import { MetadataFragmentComponent } from '../projects/metadata-fragment/metadata-fragment.component';

@Component({
  selector: 'app-project-details',
  imports: [CommonModule, MatIconModule, AgreementsFragmentComponent, MetadataFragmentComponent],
  templateUrl: './project-details.component.html',
  styleUrl: './project-details.component.scss'
})
export class ProjectDetailsComponent {

  projectId!: string;
  project: any; 
  phases = [
    { name: 'Project Creation', status: 'Pending' },
    { name: 'Legal Agreements', status: 'Pending' },
    { name: 'Metadata Submission', status: 'Pending' },
    { name: 'Data Submission', status: 'Pending' }
  ];
  currentPhaseIndex = 0;  // for example, "Legal Agreements" is active

  constructor(private route: ActivatedRoute, private projectService: ProjectService) {}

  ngOnInit(): void {
    this.projectId = this.route.snapshot.paramMap.get('id') || '';
    // Ideally here you would fetch project full data using ProjectService
    this.projectService.getProject(this.projectId).subscribe(project => {
      this.project = project;
      console.log(this.project);
      this.setupPhasesBasedOnProjectStatus();
    });
  }

  setupPhasesBasedOnProjectStatus() {
    const stageMap: { [key: string]: number } = {
      'P': 0, // Project Creation
      'A': 1, // Legal Agreements
      'M': 2, // Metadata Submission
      'D': 3,  // Data Submission
      'DONE': 4 // Completed
    };

    const mainStage = this.project.status.split('-')[0]; 
    const subStage = this.project.status.split('-')[1];
    this.currentPhaseIndex = stageMap[mainStage] || 0;

    // Update phase statuses dynamically
    
    console.log(this.phases[this.currentPhaseIndex]);
  }

  get convertedStatus() {
    return convertStatus(this.project.status);
  }

  validateCurrentStep() {
    if (this.currentPhaseIndex < this.phases.length) {
      this.projectService.updateProjectStatus(this.projectId, this.getNextPhaseStatusSuccess(this.phases[this.currentPhaseIndex].name)).subscribe(() => {
        console.log('Project status updated successfully!');
        this.phases[this.currentPhaseIndex].status = 'Approved';
        this.currentPhaseIndex++;
      });
    }
  }

  getNextPhaseStatusSuccess(phaseName: string): string {
    const phaseStatusMap: { [key: string]: string } = {
      'Project Creation': "A-E",
      'Legal Agreements': 'M-E',
      'Metadata Submission': 'D-E',
      'Data Submission': 'DONE'
    };
    return phaseStatusMap[phaseName] || 'P-E';
  }

  getNextPhaseStatusFailure(phaseName: string): string {
    const phaseStatusMap: { [key: string]: string } = {
      'Project Creation': "P-R",
      'Legal Agreements': 'A-R',
      'Metadata Submission': 'M-R',
    };
    return phaseStatusMap[phaseName] || 'P-R';
  }

  rejectCurrentStep() {
    if (this.currentPhaseIndex < this.phases.length) {
      this.phases[this.currentPhaseIndex].status = 'Rejected';
      this.projectService.updateProjectStatus(this.projectId, this.getNextPhaseStatusFailure(this.phases[this.currentPhaseIndex].name)).subscribe(() => {
        console.log('Project status updated to Rejected!');
      });
    }
    this.setupPhasesBasedOnProjectStatus();
  }

}
