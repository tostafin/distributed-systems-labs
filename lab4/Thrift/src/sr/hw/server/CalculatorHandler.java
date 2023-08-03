package sr.hw.server;

import org.apache.thrift.TException;
import sr.rpc.thrift.Calculator;
import sr.rpc.thrift.InvalidOperation;

import java.util.List;

public class CalculatorHandler implements Calculator.Iface {

	int id;

	public CalculatorHandler(int id) {
		this.id = id;
	}

	@Override
	public int add(int n1, int n2) {
		System.out.println("CalcHandler#" + id + " add(" + n1 + "," + n2 + ")");
		if(n1 > 1000 || n2 > 1000) { 
			try { Thread.sleep(6000); } catch(InterruptedException ex) { }
			System.out.println("DONE");
		}
		return n1 + n2;
	}

	@Override
	public int subtract(int num1, int num2) throws TException {
		System.out.println("CalcHandler#" + id + " subtract(" + num1 + "," + num2 + ")");
		if(num1 > 1000 || num2 > 1000) {
			try { Thread.sleep(6000); } catch(InterruptedException ex) { }
			System.out.println("DONE");
		}
		return num1 - num2;
	}

	@Override
	public double avg(List<Double> numbers) throws InvalidOperation, TException {
		double sum = 0;
		for (double n : numbers) {
			sum += n;
		}
		return sum / numbers.size();
	}
}
