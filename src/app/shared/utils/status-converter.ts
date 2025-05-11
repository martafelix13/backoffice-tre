export function convertStatus(code: string): string {
    const [mainStatus, subStatus] = code.split('-');
  
    const mainStatusMap: { [key: string]: string } = {
      P: 'Project',
      M: 'Metadata',
      L: 'Legal Agreements',
      D: 'Data Submission'
      // Add more if needed
    };
  
    const subStatusMap: { [key: string]: string } = {
      AR: 'Awaiting Review',
      E: 'Editing'
    };
  
    const mainText = mainStatusMap[mainStatus] || 'Unknown Stage';
    const subText = subStatusMap[subStatus] || 'Unknown Sub-status';
  
    return `${mainText} - ${subText}`;
  }
  