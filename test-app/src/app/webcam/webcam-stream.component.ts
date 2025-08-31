import { Component } from '@angular/core';
import { OnInit, OnDestroy } from '@angular/core';

import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-webcam-stream',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div style="width: 85vw; height: 70vh; display: flex; align-items: center; justify-content: center;">
      <img *ngIf="showStream" [src]="streamUrl" width="1050" height="600" alt="Webcam Stream"
        style="max-width: 100%; max-height: 100%; object-fit: contain;" />
    </div>
  `
})
export class WebcamStreamComponent implements OnInit, OnDestroy {
  streamUrl = 'http://192.168.1.5/cam/index2.php?get=1';
  showStream = true;

  ngOnInit() {
    this.showStream = true;
  }

  ngOnDestroy() {
    this.showStream = false;
  }
}
