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
        { label: 'Receipt', link: '/main-page/app-recipe-table' },
        { label: 'Widget', link: '/main-page/widget' }
      ],
      expanded: false
    },

    {
      label: 'Home telemetry',
      items: [
        { label: 'CAM', link: '/cam' },
        { label: 'Kotel', link: '/cotel' }
      ],
      expanded: false
    },

    {
      label: 'Wending',
      items: [
        { label: 'Машини', link: '/machines' },
        { label: 'Рецепти', link: '/machines' },
        { label: 'Інградієнти', link: '/receipts' },
        { label: 'Файли обновлень', link: '/receipts' }
      ],
      expanded: false
    },
    {
      label: 'Setup',
      items: [
        { label: 'Users', link: '/users' },
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
