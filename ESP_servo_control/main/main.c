#include <stdio.h>
#include <string.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"
#include "driver/ledc.h"

#define UART_PC     UART_NUM_0   // USB (ROS + monitor)
#define UART_DEBUG  UART_NUM_2   // Pines físicos

#define BUF_SIZE 1024

int duty = 1638; // The duty will vary from 1638 to 3276

void servo_init(void *arg)
{
    
    ledc_timer_config_t timer_conf = {
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .timer_num = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_15_BIT,
        .freq_hz = 50, // 50 Hz for servo control
        .clk_cfg = LEDC_AUTO_CLK
    };

    ledc_timer_config(&timer_conf); // Configure LEDC timer

    ledc_channel_config_t channel_conf = {
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0,
        .timer_sel = LEDC_TIMER_0,
        .intr_type = LEDC_INTR_DISABLE,
        .gpio_num = 25, // GPIO pin connected to servo signal
        .duty = duty
    };
    ledc_channel_config(&channel_conf); // Configure LEDC channel
}

void uart_init_all(void)
{
    // === UART0 (USB) ===
    uart_config_t uart_config_0 = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };

    uart_driver_install(UART_PC, BUF_SIZE, 0, 0, NULL, 0);
    uart_param_config(UART_PC, &uart_config_0);

    // === UART2 (GPIO16 RX, GPIO17 TX) ===
    uart_config_t uart_config_2 = uart_config_0;

    uart_driver_install(UART_DEBUG, BUF_SIZE, 0, 0, NULL, 0);
    uart_param_config(UART_DEBUG, &uart_config_2);

    uart_set_pin(UART_DEBUG, 17, 16, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
}

void app_main(void)
{
    uart_init_all();
    servo_init(NULL);

    uint8_t data[BUF_SIZE];


    while (1)
    {
        int len = uart_read_bytes(UART_PC, data, BUF_SIZE - 1, 20 / portTICK_PERIOD_MS);

        if (len > 0)
        {
            data[len] = '\0';

            float angles[5];

            int parsed = sscanf((char*)data, "%f,%f,%f,%f,%f",
                                &angles[0], &angles[1], &angles[2],
                                &angles[3], &angles[4]);

            if (parsed == 5)
            {
                char msg[200];
                int msg_len = sprintf(msg,
                    "Angles: %.2f %.2f %.2f %.2f %.2f\n",
                    angles[0], angles[1], angles[2],
                    angles[3], angles[4]);
                
                int rotate = 1638 + (int)(angles[1] * (3276 - 1638) / 180.0);

                ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, rotate);
                ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);

                // Mostrar en monitor (USB)
                uart_write_bytes(UART_PC, msg, msg_len);

                // duplicar a UART2
                uart_write_bytes(UART_DEBUG, msg, msg_len);
            }
            else
            {
                char *err = "Parse error\n";
                uart_write_bytes(UART_PC, err, strlen(err));
                uart_write_bytes(UART_DEBUG, err, strlen(err));
            }
        }

        vTaskDelay(10 / portTICK_PERIOD_MS);
    }
}