// Auto-dismiss flash messages (if added in future)
document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => el.remove(), 4000);
});

// Highlight today's date rows
document.querySelectorAll('.table td:first-child').forEach(td => {
    const today = new Date().toISOString().slice(0, 10);
    if (td.textContent.trim().startsWith(today)) {
        td.closest('tr').style.background = '#f0fdf4';
    }
});

document.querySelectorAll('.js-abrir-baixa').forEach(button => {
    button.addEventListener('click', () => {
        const contaId = Number(button.dataset.contaId);
        const descricao = button.dataset.contaDescricao || '';
        const valor = Number(button.dataset.contaValor || 0);
        const valorPago = Number(button.dataset.contaValorPago || 0);
        abrirBaixa(contaId, descricao, valor, valorPago);
    });
});
