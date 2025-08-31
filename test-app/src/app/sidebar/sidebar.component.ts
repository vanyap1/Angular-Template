import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent {
  isCollapsed = false;

  menuItems = [
    {
      label: 'Main',
      items: [
        
        { label: 'Бойлер', link: '/main-page/boiler-scheduler' },
        { label: 'Widget', link: '/main-page/widget' },
        { label: 'Сенсори', link: '/main-page/sensor-dashboard' }
      ],
      expanded: false
    },

    {
      label: 'Home telemetry',
      items: [
        { label: 'CAM', link: '/main-page/webcam' },
        { label: 'Kotel', link: '/kotel' }
      ],
      expanded: false
    },

    {
      label: 'Wending',
      items: [
        { label: 'Машини', link: '/machines' },
        { label: 'Рецепти', link: '/main-page/userEditor' },
        { label: 'Інградієнти', link: '/receipts' },
        { label: 'Файли обновлень', link: '/receipts' }
      ],
      expanded: false
    },
    {
      label: 'Setup',
      items: [
        { label: 'Користувачі', link: '/main-page/app-userEditor' },
        { label: 'Settings', link: '/settings' }
      ],
      expanded: false
    }
  ];

  toggleGroup(index: number) {
    this.menuItems[index].expanded = !this.menuItems[index].expanded;
  }

  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
  }
}
