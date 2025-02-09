import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-widget',
  templateUrl: './widget.component.html',
  styleUrls: ['./widget.component.css'],
  standalone: true,
  imports: [FormsModule]
})
export class WidgetComponent {
  inputText: string = '';
  outputText: string = '';

  constructor(private http: HttpClient) {}

  onButtonClick() {
    this.http.get(`/api/param/?id=${this.inputText}`, { responseType: 'text' })
    .subscribe(
      response => {
        console.log('Response from server:', response);
        this.outputText = response;
      },
      error => {
        console.error('Error occurred:', error);
      }
    );
  }
}