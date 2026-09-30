// SISTEMA INTELIGENTE DE GESTION DE PARQUEO VEHICULAR
// Usa: funciones, if/switch, do-while/for y matrices dinamicas (new / delete)
#include <iostream>
using namespace std;

// Tipo de espacio: 1=Auto, 2=Moto, 3=Discapacitado
// En la matriz placa: 0 = espacio libre, otro numero = placa del vehiculo

int **crearMatriz(int F, int C) {
    int **m = new int*[F];
    for (int i = 0; i < F; i++) {
        m[i] = new int[C];
        for (int j = 0; j < C; j++)
            m[i][j] = 0;  // inicia en ceros
    }
    return m;
}

void liberarMatriz(int **m, int F) {
    for (int i = 0; i < F; i++) delete[] m[i];
    delete[] m;
}

// 1. Registro de espacios: tipo de cada espacio de la matriz
void registrarEspacios(int **tipo, int F, int C) {
    cout << "Tipo de cada espacio (1=Auto, 2=Moto, 3=Discapacitado)\n";
    for (int i = 0; i < F; i++)
        for (int j = 0; j < C; j++)
            do {
                cout << "Espacio [" << i << "][" << j << "]: ";
                cin >> tipo[i][j];
            } while (tipo[i][j] < 1 || tipo[i][j] > 3);
}

// Muestra el parqueo: letra del tipo + L (libre) u O (ocupado)
void mostrarParqueo(int **tipo, int **placa, int F, int C) {
    char letra[4] = {' ', 'A', 'M', 'D'};
    cout << "A=Auto M=Moto D=Discapacitado | L=Libre O=Ocupado\n";
    for (int i = 0; i < F; i++) {
        for (int j = 0; j < C; j++) {
            cout << letra[tipo[i][j]];
            if (placa[i][j] == 0) cout << "L\t";
            else cout << "O\t";
        }
        cout << endl;
    }
}

// 2. Ingreso: pide placa y hora, asigna el primer espacio libre del tipo.
// Devuelve 1 si ingreso el vehiculo, 0 si no habia espacio.
int ingresarVehiculo(int **tipo, int **placa, int **hora, int F, int C) {
    int t, p, h;
    do {
        cout << "Tipo de vehiculo (1=Auto, 2=Moto, 3=Discapacitado): ";
        cin >> t;
    } while (t < 1 || t > 3);
    do {
        cout << "Numero de placa: ";
        cin >> p;
    } while (p <= 0);
    do {
        cout << "Hora de ingreso (0-23): ";
        cin >> h;
    } while (h < 0 || h > 23);

    for (int i = 0; i < F; i++)
        for (int j = 0; j < C; j++)
            if (tipo[i][j] == t && placa[i][j] == 0) {
                placa[i][j] = p;
                hora[i][j] = h;
                cout << "Espacio asignado: [" << i << "][" << j << "]\n";
                return 1;
            }
    cout << "No hay espacios libres de ese tipo.\n";
    return 0;
}

// 3. Salida: calcula tiempo estacionado y pago, y libera el espacio
void salidaVehiculo(int **tipo, int **placa, int **hora, int F, int C) {
    float tarifa[4] = {0, 5, 2, 3};  // soles por hora: Auto, Moto, Discap.
    int p, h;
    cout << "Numero de placa: ";
    cin >> p;
    for (int i = 0; i < F; i++)
        for (int j = 0; j < C; j++)
            if (placa[i][j] == p && p != 0) {
                do {
                    cout << "Hora de salida (" << hora[i][j] << "-23): ";
                    cin >> h;
                } while (h < hora[i][j] || h > 23);
                int tiempo = h - hora[i][j];
                if (tiempo == 0) tiempo = 1;  // se cobra minimo 1 hora
                cout << "Tiempo estacionado: " << tiempo << " hora(s)\n";
                cout << "Pago: S/ " << tiempo * tarifa[tipo[i][j]] << endl;
                placa[i][j] = 0;  // espacio libre otra vez
                return;
            }
    cout << "Placa no encontrada.\n";
}

// 4. Reportes
void reportes(int **placa, int F, int C, int totalIngresados) {
    int libres = 0, ocupados = 0;
    for (int i = 0; i < F; i++)
        for (int j = 0; j < C; j++)
            if (placa[i][j] == 0) libres++;
            else ocupados++;
    cout << "Espacios disponibles: " << libres << endl;
    cout << "Espacios ocupados: " << ocupados << endl;
    cout << "Total vehiculos ingresados: " << totalIngresados << endl;
}

int main() {
    int F, C, opcion, total = 0;
    do {
        cout << "Numero de filas (1-10): ";
        cin >> F;
    } while (F < 1 || F > 10);
    do {
        cout << "Numero de columnas (1-10): ";
        cin >> C;
    } while (C < 1 || C > 10);

    int **tipo = crearMatriz(F, C);
    int **placa = crearMatriz(F, C);
    int **hora = crearMatriz(F, C);
    registrarEspacios(tipo, F, C);

    do {
        cout << "\n===== PARQUEO =====\n";
        cout << "1. Ver parqueo\n";
        cout << "2. Ingreso de vehiculo\n";
        cout << "3. Salida de vehiculo\n";
        cout << "4. Reportes\n";
        cout << "5. Salir\n";
        cout << "Seleccione una opcion: ";
        cin >> opcion;
        switch (opcion) {
        case 1: mostrarParqueo(tipo, placa, F, C); break;
        case 2: total = total + ingresarVehiculo(tipo, placa, hora, F, C); break;
        case 3: salidaVehiculo(tipo, placa, hora, F, C); break;
        case 4: reportes(placa, F, C, total); break;
        case 5: cout << "Saliendo...\n"; break;
        default: cout << "Opcion invalida!\n";
        }
    } while (opcion != 5);

    liberarMatriz(tipo, F);
    liberarMatriz(placa, F);
    liberarMatriz(hora, F);
    return 0;
}
