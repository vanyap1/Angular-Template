import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebcamStreamComponent } from './webcam-stream.component';

@NgModule({
  imports: [CommonModule, WebcamStreamComponent],
  exports: [WebcamStreamComponent]
})
export class WebcamModule {}
