package employeesDAO;

import java.util.List;

public class EmployeesDAOTest {

	public static void main(String[] args) {

		EmployeesDAO dao = new EmployeesDAO();
		List<Employee> employeeList = dao.findAll();
		

//		// リストからEmployeeデータを繰り返し取り出し表示
//		for (Employee emp : employeeList) {
//			System.out.println(emp);
//		}

	}

}
