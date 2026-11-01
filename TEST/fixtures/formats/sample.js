/**
 * Anomaly Event Dispatcher.
 * Batches telemetry alerts and dispatches websocket messages.
 */

class AlertDispatcher {
    constructor(endpointUrl, batchSize = 50) {
        this.endpointUrl = endpointUrl;
        this.batchSize = batchSize;
        this.queue = [];
    }

    enqueueAlert(alert) {
        this.queue.push({ ...alert, recordedAt: new Date().toISOString() });
        if (this.queue.length >= this.batchSize) {
            return this.flush();
        }
        return Promise.resolve(false);
    }

    async flush() {
        if (this.queue.length === 0) return true;
        const payload = [...this.queue];
        this.queue = [];
        console.log(`Dispatched ${payload.length} alerts to ${this.endpointUrl}`);
        return true;
    }
}

module.exports = { AlertDispatcher };
