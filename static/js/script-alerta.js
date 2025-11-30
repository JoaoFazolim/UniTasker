document.addEventListener('DOMContentLoaded', function() {
            const alerts = document.querySelectorAll('.alert');
            
            alerts.forEach(alert => {
                //Espera 4 segundos (4000ms)
                setTimeout(() => {
                    //Adiciona classe que diminui a opacidade
                    alert.classList.add('alert-hiding');
                    
                    //Espera a transição do CSS terminar (0.5s) e remove do HTML
                    setTimeout(() => {
                        alert.remove();
                    }, 500);
                }, 6000);
            });
        });