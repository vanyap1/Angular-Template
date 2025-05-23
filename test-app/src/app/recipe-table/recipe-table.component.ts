import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { PopupDialogComponent } from '../popup-dialog/popup-dialog.component';

@Component({
  selector: 'app-recipe-table',
  standalone: true,
  templateUrl: './recipe-table.component.html',
  styleUrls: ['./recipe-table.component.css'],
  imports: [CommonModule, FormsModule, HttpClientModule, MatDialogModule, MatButtonModule]
})
export class RecipeTableComponent {
  @Input() tableData: any[] = [];
  @Output() tableDataChange = new EventEmitter<any[]>();

  // Змінна для зберігання даних таблиці
  editingRowIndex: number | null = null;
  tempData: any = {};

  constructor(private http: HttpClient, public dialog: MatDialog) {}

  // ініціалізація
  ngOnInit(): void {
    // Заглушка для даних API
    this.tableData = [
      { id: 1, name: 'John', age: 28, job: 'Developer' },
      { id: 2, name: 'Jane', age: 34, job: 'Designer' },
      { id: 3, name: 'Mike', age: 25, job: 'Manager' },
      { id: 4, name: 'Anna', age: 22, job: 'Intern' }
    ];
  }

  // Перемикання між режимом редагування і перегляду
  startEditing(rowIndex: number) {
    this.editingRowIndex = rowIndex;
    this.tempData = { ...this.tableData[rowIndex] };
  }

  // Збереження змін
  saveChanges(rowIndex: number) {
    this.tableData[rowIndex] = { ...this.tempData };
    this.editingRowIndex = null;
    this.tableDataChange.emit(this.tableData);
  }

  // Додавання нового рядка
  addRow() {
    const newRow = { id: this.tableData.length + 1, name: '', age: null, job: '' };
    this.tableData.push(newRow);
    this.startEditing(this.tableData.length - 1);
    this.tableDataChange.emit(this.tableData);
  }

  // Видалення рядка
  deleteRow(rowIndex: number) {
    this.tableData.splice(rowIndex, 1);
    this.tableDataChange.emit(this.tableData);
  }

  sendTableData() {
    const tableDataJson = JSON.stringify(this.tableData);
    const encodedTableData = encodeURIComponent(tableDataJson);
    this.http.get(`/api/param/?id=${encodedTableData}`, { responseType: 'text' })
      .subscribe(
        response => {
          console.log('Response from server:', response);
          this.openDialog(response);
        },
        error => {
          console.error('Error occurred:', error);
        }
      );
  }
  
  openDialog(response: string): void {
    this.dialog.open(PopupDialogComponent, {
      data: response
    });
  }
}