import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';
import { provideCharts, withDefaultRegisterables } from 'ng2-charts';
import { MatNativeDateModule } from '@angular/material/core';


@Component({
  selector: 'app-sensor-dashboard',
  standalone: true,
  templateUrl: './sensor-dashboard.component.html',
  styleUrls: ['./sensor-dashboard.component.css'],
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatTableModule,
    MatDatepickerModule,
    MatInputModule,
    MatFormFieldModule,
  MatIconModule,
  MatSlideToggleModule,
  MatDividerModule,
  MatTooltipModule,
  BaseChartDirective,
  MatNativeDateModule
  ],
  providers: [
    provideCharts(withDefaultRegisterables())
  ]
})
export class SensorDashboardComponent implements OnInit {
  sensors: any[] = [];
  selectedSensor: any = null;
  historyRows: any[] = [];
  startDate: Date = new Date();
  endDate: Date = new Date();
  channelsCollapsed = false;
  displayedColumns: string[] = [
    'recorded_at',
    'channel1',
    'channel2',
    'channel3',
    'channel4',
    'channel5',
    'channel6',
    'channel7',
    'channel8'
  ];

  channelSelection: boolean[] = [true, true, false, false, false, false, false, false];
  chartData: any[] = [];
  chartLabels: string[] = [];
  chartOptions = { responsive: true };

  lastMeasurements: { [mac: string]: any } = {};

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.setDefaultDates();
    this.loadSensors();
  }

  setDefaultDates() {
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    this.startDate = yesterday;
    this.endDate = now;
  }

  formatDateTime(date: Date): string {
    // Формат: YYYY-MM-DD HH:mm:ss
    const pad = (n: number) => n < 10 ? '0' + n : n;
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  }

  loadSensors() {
    this.http.get<any>('/api/sensors/').subscribe({
      next: res => {
        this.sensors = res.ok || [];
        // Fetch last measurements for each sensor
        this.sensors.forEach((sensor: any) => {
          const mac = encodeURIComponent(sensor.mac);
          this.http.get<any>(`/api/sensor/${mac}/last/`).subscribe({
            next: lastRes => {
              this.lastMeasurements[sensor.mac] = lastRes.ok || {};
            },
            error: err => {
              this.lastMeasurements[sensor.mac] = null;
            }
          });
        });
      },
      error: err => {
        alert('Помилка завантаження сенсорів');
      }
    });
  }

  showHistory(sensor: any) {
    this.selectedSensor = sensor;
    const mac = encodeURIComponent(sensor.mac);
    const params = `start=${encodeURIComponent(this.formatDateTime(this.startDate))}&end=${encodeURIComponent(this.formatDateTime(this.endDate))}`;
    this.http.get<any>(`/api/sensor/${mac}/history/?${params}`).subscribe({
      next: res => {
        const rows = res.ok?.rows || [];
        this.historyRows = rows;
        this.chartLabels = rows.map((r: any) => r.recorded_at);
        const allChannels = [
          { data: rows.map((r: any) => r.channel1), label: 'Канал 1' },
          { data: rows.map((r: any) => r.channel2), label: 'Канал 2' },
          { data: rows.map((r: any) => r.channel3), label: 'Канал 3' },
          { data: rows.map((r: any) => r.channel4), label: 'Канал 4' },
          { data: rows.map((r: any) => r.channel5), label: 'Канал 5' },
          { data: rows.map((r: any) => r.channel6), label: 'Канал 6' },
          { data: rows.map((r: any) => r.channel7), label: 'Канал 7' },
          { data: rows.map((r: any) => r.channel8), label: 'Канал 8' }
        ];
        this.chartData = allChannels.filter((_, i) => this.channelSelection[i]);
      },
      error: err => {
        alert('Помилка завантаження історії');
      }
    });
  }

  toggleChannel(index: number) {
    // Refresh chart if sensor selected
    if (this.selectedSensor) {
      this.showHistory(this.selectedSensor);
    }
  }
}