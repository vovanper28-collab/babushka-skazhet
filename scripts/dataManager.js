const DataManager = (function() {
    let data = null;

    async function load() {
        try {
            const response = await fetch('/data/phrases.json');
            if (!response.ok) {
                throw new Error('Не удалось загрузить данные');
            }
            const jsonData = await response.json();
            data = jsonData;
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
            throw error;
        }
    }
    
    return {
        load,
        get() {
            return data;
        }
    };
})();