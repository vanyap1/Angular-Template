import { Injectable } from '@angular/core';

export interface NotificationMessage {
  id: number;
  message: string;
  type: 'ok' | 'error' | 'warning';
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private notificationComponent: any;
  private idCounter = 0;

  register(component: any) {
    this.notificationComponent = component;
  }

  show(message: string, type: 'ok' | 'error' | 'warning' = 'ok') {
    if (this.notificationComponent) {
      this.notificationComponent.addNotification({
        id: ++this.idCounter,
        message,
        type
      });
    }
  }
}
