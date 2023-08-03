package sr.hw.server;

import org.apache.thrift.TMultiplexedProcessor;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TCompactProtocol;
import org.apache.thrift.protocol.TProtocolFactory;
import org.apache.thrift.server.TServer;
import org.apache.thrift.server.TServer.Args;
import org.apache.thrift.server.TSimpleServer;
import org.apache.thrift.transport.TServerSocket;
import org.apache.thrift.transport.TServerTransport;
import sr.rpc.thrift.AdvancedCalculator;
import sr.rpc.thrift.Calculator;
import sr.thrift.server.AdvancedCalculatorHandler;

// Generated code


public class ThriftServer {


	public static void main(String [] args) 
	{
		try {	
			Runnable simple = new Runnable() {
				public void run() {
					simple();
				}
			};      
			Runnable multiplex = new Runnable() {
				public void run() {
					multiplex();
				}
			};

			new Thread(simple).start();
			new Thread(multiplex).start();

		} catch (Exception x) {
			x.printStackTrace();
		}
	}

	
	public static void simple() 
	{
		try {
			Calculator.Processor<CalculatorHandler> processor1 = new Calculator.Processor<CalculatorHandler>(new CalculatorHandler(1));
			Calculator.Processor<CalculatorHandler> processor2 = new Calculator.Processor<CalculatorHandler>(new CalculatorHandler(2));
			AdvancedCalculator.Processor<AdvancedCalculatorHandler> processor3 = new AdvancedCalculator.Processor<AdvancedCalculatorHandler>(new AdvancedCalculatorHandler(11));
			
			TServerTransport serverTransport = new TServerSocket(9080);
			
			//TProtocolFactory protocolFactory = new TBinaryProtocol.Factory();
			//TProtocolFactory protocolFactory = new TJSONProtocol.Factory();
			TProtocolFactory protocolFactory = new TCompactProtocol.Factory();
			
			TServer server1 = new TSimpleServer(new Args(serverTransport).protocolFactory(protocolFactory).processor(processor1));
			//TServer server2 = new TSimpleServer(new Args(serverTransport).protocolFactory(protocolFactory).processor(processor2));
			//TServer server3 = new TSimpleServer(new Args(serverTransport).protocolFactory(protocolFactory).processor(processor3));

			System.out.println("Starting the simple server...");
			server1.serve();
			//server2.serve();
			//server3.serve();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	
	public static void multiplex() 
	{
		try {
			Calculator.Processor<CalculatorHandler> processor1 = new Calculator.Processor<CalculatorHandler>(new CalculatorHandler(1));
			Calculator.Processor<CalculatorHandler> processor2 = new Calculator.Processor<CalculatorHandler>(new CalculatorHandler(2));
			AdvancedCalculator.Processor<AdvancedCalculatorHandler> processor3 = new AdvancedCalculator.Processor<AdvancedCalculatorHandler>(new AdvancedCalculatorHandler(11));
			AdvancedCalculator.Processor<AdvancedCalculatorHandler> processor4 = new AdvancedCalculator.Processor<AdvancedCalculatorHandler>(new AdvancedCalculatorHandler(12));

			TServerTransport serverTransport = new TServerSocket(9090);

			TProtocolFactory protocolFactory = new TBinaryProtocol.Factory();
			//TProtocolFactory protocolFactory = new TJSONProtocol.Factory();
			//TProtocolFactory protocolFactory = new TCompactProtocol.Factory();
			
			TMultiplexedProcessor multiplex = new TMultiplexedProcessor();
            multiplex.registerProcessor("S1", processor1);
            multiplex.registerProcessor("S2", processor2);
            multiplex.registerProcessor("A1", processor3);
            multiplex.registerProcessor("A2", processor4);

			TServer server = new TSimpleServer(new Args(serverTransport).protocolFactory(protocolFactory).processor(multiplex)); 
			
			System.out.println("Starting the multiplex server...");
			server.serve(); 
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}