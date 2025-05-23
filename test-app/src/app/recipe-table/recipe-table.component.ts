import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { PopupDialogComponent } from '../popup-dialog/popup-dialog.component';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';

@Component({
  selector: 'app-recipe-table',
  standalone: true,
  templateUrl: './recipe-table.component.html',
  styleUrls: ['./recipe-table.component.css'],
  imports: [CommonModule, FormsModule, MatDialogModule, MatButtonModule]
})
export class RecipeTableComponent {
  @Input() tableData: any[] = [];
  @Output() tableDataChange = new EventEmitter<any[]>();

  editingRowIndex: number | null = null;
  tempData: any = {};

  // Додаємо NotificationService у конструктор
  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    const token = this.authService.getToken();
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<any[]>('/api/users/', { headers })
      .subscribe({
        next: data => {
          this.tableData = data;
          this.tableDataChange.emit(this.tableData);
        },
        error: error => {
          this.notificationService.show('Помилка завантаження користувачів', 'error');
        }
      });
  }

  startEditing(rowIndex: number) {
    this.editingRowIndex = rowIndex;
    this.tempData = { ...this.tableData[rowIndex] };
  }

  saveChanges(rowIndex: number) {
    const user = { ...this.tempData };
    const token = this.authService.getToken();
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    if (!user.id) {
      const password = user.password || 'defaultpass';
      this.http.post<any>(
        `/api/userAdd/?login=${encodeURIComponent(user.login)}&password=${encodeURIComponent(password)}&user_level=${user.user_level}&user_group=${encodeURIComponent(user.user_group)}`,
        {},
        { headers }
      ).subscribe({
        next: response => {
          this.tableData[rowIndex] = { ...user, id: response.id };
          this.editingRowIndex = null;
          this.tableDataChange.emit(this.tableData);
          this.notificationService.show('Користувача додано!', 'ok');
        },
        error: error => {
          this.notificationService.show('Помилка при додаванні користувача', 'error');
        }
      });
    } else {
      const password = user.password || 'defaultpass';
      this.http.put<any>(
        `/api/userEdit/${user.id}?login=${encodeURIComponent(user.login)}&password=${encodeURIComponent(password)}&user_level=${user.user_level}&user_group=${encodeURIComponent(user.user_group)}`,
        {},
        { headers }
      ).subscribe({
        next: response => {
          this.tableData[rowIndex] = user;
          this.editingRowIndex = null;
          this.tableDataChange.emit(this.tableData);
          this.notificationService.show('Користувача оновлено!', 'ok');
        },
        error: error => {
          this.notificationService.show('Помилка при оновленні користувача', 'error');
        }
      });
    }
  }

  addRow() {
    const newRow = { id: null, login: '', user_level: null, user_group: '' };
    this.tableData.push(newRow);
    this.startEditing(this.tableData.length - 1);
    this.tableDataChange.emit(this.tableData);
  }

  deleteRow(rowIndex: number) {
    const user = this.tableData[rowIndex];
    if (!user.id) {
      this.tableData.splice(rowIndex, 1);
      this.tableDataChange.emit(this.tableData);
      return;
    }

    const token = this.authService.getToken();
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.delete<any>(`/api/userDel/${user.id}`, { headers })
      .subscribe({
        next: response => {
          this.tableData.splice(rowIndex, 1);
          this.tableDataChange.emit(this.tableData);
          this.notificationService.show('Користувача видалено!', 'ok');
        },
        error: error => {
          this.notificationService.show('Помилка при видаленні користувача', 'error');
        }
      });
  }

  cancelEdit() {
    this.editingRowIndex = null;
  }

  sendTableData() {
    const tableDataJson = JSON.stringify(this.tableData);
    const encodedTableData = encodeURIComponent(tableDataJson);
    this.http.get(`/api/param/?id=${encodedTableData}`, { responseType: 'text' })
      .subscribe({
        next: response => {
          this.openDialog(response);
          this.notificationService.show('Дані таблиці відправлено!', 'ok');
        },
        error: error => {
          this.notificationService.show('Помилка при відправці таблиці', 'error');
        }
      });
  }

  openDialog(response: string): void {
    //this.dialog.open(PopupDialogComponent, {
    //  data: response
    //});
  }
}
