import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDialogModule } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-boiler-scheduler',
  standalone: true,
  templateUrl: './boiler-scheduler.component.html',
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatInputModule,
    MatSlideToggleModule,
    MatIconModule,
    MatFormFieldModule,
    MatSelectModule,
    MatDialogModule,
    MatTooltipModule,
    MatNativeDateModule
  ]
})
export class BoilerSchedulerComponent implements OnInit {
  displayedColumns: string[] = [
    'day_name', 'start_time', 'stop_time', 'enabled', 'comment', 'actions'
  ];
  scheduleData: any[] = [];
  editingRowIndex: number | null = null;
  tempData: any = {};

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadSchedule();
  }

  loadSchedule() {
    this.http.get<any>('/api/water_heater_schedule/')
      .subscribe({
        next: res => {
          this.scheduleData = res.ok || [];
        },
        error: err => {
          // Додайте сервіс для нотифікацій, якщо потрібно
          alert('Помилка завантаження розкладу');
        }
      });
  }

  startEditing(rowIndex: number) {
    this.editingRowIndex = rowIndex;
    this.tempData = { ...this.scheduleData[rowIndex] };
  }

  saveChanges(rowIndex: number) {
  const item = this.tempData;
  const params = new URLSearchParams({
    start_time: item.start_time,
    stop_time: item.stop_time,
    enabled: item.enabled,
    userKey: 'key'
  } as any).toString();

  this.http.put<any>(
    `/api/water_heater_schedule/${item.id}?${params}`,
    {}
  ).subscribe({
    next: res => {
      this.editingRowIndex = null;
      this.loadSchedule(); // Перезавантажити дані після збереження
    },
    error: err => {
      alert('Помилка при збереженні');
    }
  });
}

  cancelEdit() {
    this.editingRowIndex = null;
  }
}