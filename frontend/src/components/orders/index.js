import styles from './styles.module.css'
import { Icons } from '..'

const Orders = ({ orders }) => {
  return <div className={styles.orders}>
    <Icons.Cart />
  </div>
}

export default Orders
