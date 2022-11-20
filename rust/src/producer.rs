use amiquip::{Connection, Exchange, Publish, Result};

fn main() -> Result<()> {
    // Open connection.
    let mut connection = Connection::insecure_open("amqp://orson:orson@localhost:8001")?;

    // Open a channel - None says let the library choose the channel ID.
    let channel = connection.open_channel(None)?;

    // Get a handle to the direct exchange on our channel.
    let exchange = Exchange::direct(&channel);

    // Publish a message to the "hello" queue.
    exchange.publish(Publish::new("hello there".as_bytes(), "hello"))?;

    connection.close()
}
