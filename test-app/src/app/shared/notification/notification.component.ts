import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationMessage } from '../../services/notification.service';

@Component({
  selector: 'app-notification',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="notification"
         *ngFor="let n of notifications"
         [ngClass]="n.type">
      {{ n.message }}
      <span class="close-btn" (click)="removeNotification(n.id)">&times;</span>
    </div>
  `,
  styleUrls: ['./notification.component.css']
})
export class NotificationComponent {
  notifications: NotificationMessage[] = [];

  addNotification(notification: NotificationMessage) {
    this.notifications.push(notification);
    setTimeout(() => this.removeNotification(notification.id), 4000);
  }

  removeNotification(id: number) {
    this.notifications = this.notifications.filter(n => n.id !== id);
  }
}
